import asyncio
import json
import logging
import os
from typing import AsyncGenerator

import numpy as np
from app.core.config import config
from google import generativeai as genai
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from pydantic.v1 import SecretStr
from app.schemas.stream import StreamMarkers
from dotenv import load_dotenv

load_dotenv()
from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services import render_service

# pyright: reportPrivateImportUsage=false
# Configure Gemini embedding model

genai.configure(api_key=config.GEMINI_API_KEY)
logger = logging.getLogger(__name__)

class CodeStreamCallback(AsyncCallbackHandler):
    """Callback handler for streaming code generation"""

    def __init__(self):
        self.queue = asyncio.Queue()
        self.error_occurred = False

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Handle new token from LLM"""
        await self.queue.put(token)

    async def on_llm_end(self, response, **kwargs) -> None:
        """Handle LLM completion"""
        await self.queue.put(StreamMarkers.STREAM_END)

    async def on_llm_error(self, error, **kwargs) -> None:
        """Handle LLM error"""

        await self.queue.put(f"{StreamMarkers.STREAM_ERROR} {str(error)}")
        logger.error(f"LLM error: {str(error)}")

    async def put_custom_error(self, message: str):
        """customer error message (for use in inference method)"""

        await self.queue.put(f"{StreamMarkers.STREAM_ERROR} {str(message)}")
        await self.queue.put(StreamMarkers.STREAM_END)

    async def astream(self) -> AsyncGenerator[str, None]:
        """Stream tokens from the queue"""
        while True:
            token = await self.queue.get()
            if token == StreamMarkers.STREAM_END:
                break
            yield token




class ChainManager:
    def __init__(self):
        self.embedding_model = genai.get_model("models/embedding-001")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_path = os.path.join(base_dir, "..", "..", "cleaned_index_mapping.json")

        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
            self.documents = [Document(page_content=d["content"]) for d in doc_data]
            self.doc_embeddings = [
                self._embed_with_gemini(doc.page_content) for doc in self.documents
            ]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load document mapping: {e}")

    def _embed_with_gemini(self, text: str) -> np.ndarray:
        try:
            res = self.embedding_model.embed_content(
                content=text,
                task_type="retrieval_document",
                title="RAG chunk",
            )
            return np.array(res["embedding"], dtype=np.float32)
        except Exception:
            return np.zeros(3072, dtype=np.float32)  # Safe fallback

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return np.clip(np.dot(a, b) / denom, -1.0, 1.0)

    def _retrieve_top_k(
        self, query: str, documents: list[Document], k: int = 10
    ) -> list[Document]:
        query_emb = self._embed_with_gemini(query)
        similarities = [
            self._cosine_similarity(query_emb, doc_emb)
            for doc_emb in self.doc_embeddings
        ]
        top_indices = np.argsort(similarities)[-k:][::-1]
        return [documents[i] for i in top_indices]

    async def run_inference(self, request: InferenceRequest) -> InferenceResponse:
        query = request.prompt

        # Load LLM from .env

        llm = ChatOpenAI(
            model=config.OPENAI_LLM,
            temperature=0.1,
            api_key=SecretStr(config.OPENAI_API_KEY),
            base_url=config.OPENAI_API_BASE,
        )

        # Retrieve top-k docs
        top_k_docs = self._retrieve_top_k(query, self.documents, k=4)
        context = "\n\n".join(doc.page_content for doc in top_k_docs)

        # Prompt template
        prompt_template = self._get_prompt_template()
        final_prompt = prompt_template.format(question=query, context=context)

        response = llm.invoke(final_prompt)

        # Force extract a string from whatever comes out
        if hasattr(response, "content"):
            result_str = response.content
        elif isinstance(response, str):
            result_str = response
        elif isinstance(response, list):
            result_str = str(response[0]) if response else ""
        else:
            result_str = str(response)

        # Now Pylance will chill because it's strictly a str
        return InferenceResponse(result=str(result_str))

    async def run_inference_stream(
        self, request: InferenceRequest
    ) -> AsyncGenerator[str, None]:
        """
        Streaming inference that yields code chunks
        """
        query = request.prompt

        try:
            # Retrieve top-k docs
            top_k_docs = self._retrieve_top_k(query, self.documents, k=4)
            context = "\n\n".join(doc.page_content for doc in top_k_docs)

            # Prompt template
            prompt_template = self._get_prompt_template()
            final_prompt = prompt_template.format(question=query, context=context)

            # Create callback for streaming
            callback = CodeStreamCallback()

            # Load LLM from config - FIXED THE TYPO
            llm = ChatOpenAI(
                model=config.OPENAI_LLM,
                temperature=0.1,
                api_key=SecretStr(config.OPENAI_API_KEY),
                base_url=config.OPENAI_API_BASE,
                streaming=True,
                callbacks=[callback],
            )

            # Start the LLM inference in a background task
            async def _run_inference():
                try:
                    await llm.ainvoke(final_prompt)
                except Exception as e:
                    logger.error(f"LLM inference error: {str(e)}")
                    await callback.put_custom_error(str(e))
                finally:
                    await callback.queue.put("__END__")

            # Start the inference task
            asyncio.create_task(_run_inference())

            # Stream the results
            async for token in callback.astream():
                yield token
        except Exception as e:
            logger.error(f"Stream setup error: {str(e)}")
            yield f"{StreamMarkers.STREAM_ERROR} Stream setup error: {str(e)}"
            yield StreamMarkers.STREAM_END

    async def generate_video_from_prompt(self, prompt: str) -> str:
        # Use your own run_inference logic
        request = InferenceRequest(prompt=prompt)
        response = await self.run_inference(request)

        script = response.result
        video_path = await render_service.render_manim_script(script)
        return video_path

    def _get_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for code generation"""
        return PromptTemplate(
            input_variables=["question", "context"],
            template="""
        You are an expert Manim Community v0.19 code generator. Your job is to convert a natural language input into a valid Python animation using only the manim and math libraries.

        Critical Requirements (follow strictly):
        - Output only raw Python code. Do not use Markdown formatting, triple backticks, or any explanations.
        - Do not import any module other than manim and math.
        - Use only 1–2 character variable names.
        - Use 3D coordinate vectors for all positions: e.g., [x, y, 0]. Never use 2D coordinates.
        - Do not define helper functions or classes beyond GenScene.
        - The animation must run for at least 5 seconds.
        - The script must end with a self.play(...) call.
        - Avoid infinite loops and large memory objects.

        Base scaffold to follow exactly:

        from manim import *
        from math import *

        class GenScene(Scene):
            def construct(self):
                # Write here

        User input:
        {question}

        Relevant examples:
        {context}
        """,
        )