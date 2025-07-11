import json
import os

import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from pydantic.v1 import SecretStr  # This is from Pydantic v1 compat mode

from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.render_service import render_manim_script

# pyright: reportPrivateImportUsage=false
# Load .env values
load_dotenv()

# Configure Gemini embedding model
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "dummy"))


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
            model=os.getenv("OPENAI_LLM", "deepseek/deepseek-r1-0528:free"),
            temperature=0.1,
            api_key=SecretStr(os.getenv("OPENAI_API_KEY", "dummy")),
            base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
        )

        # Retrieve top-k docs
        top_k_docs = self._retrieve_top_k(query, self.documents, k=4)
        context = "\n\n".join(doc.page_content for doc in top_k_docs)

        # Prompt template
        prompt_template = PromptTemplate(
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

    async def generate_video_from_prompt(self, prompt: str) -> str:
        # Use your own run_inference logic
        request = InferenceRequest(prompt=prompt)
        response = await self.run_inference(request)

        script = response.result
        video_path = render_manim_script(script)
        return video_path
