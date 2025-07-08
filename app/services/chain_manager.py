import json
import os

import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.render_service import render_manim_script

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "dummy")
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
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
            # Pre-compute document embeddings
            self.doc_embeddings = [self._embed_with_gemini(doc.page_content) for doc in self.documents]
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

    def _retrieve_top_k(self, query: str, documents: list[Document], k: int = 10) -> list[Document]:
        query_emb = self._embed_with_gemini(query)
        similarities = [self._cosine_similarity(query_emb, doc_emb) for doc_emb in self.doc_embeddings]
        top_indices = np.argsort(similarities)[-k:][::-1]
        return [documents[i] for i in top_indices]

    async def run_inference(self, request: InferenceRequest) -> InferenceResponse:
        query = request.prompt

        # === Load LLM ===
        llm = ChatOpenAI(
            model="google/gemini-2.5-pro-exp-03-25",
            temperature=0.1,
        )

        # === Retrieve top-k context ===
        top_k_docs = self._retrieve_top_k(query, self.documents, k=4)
        context = "\n\n".join(doc.page_content for doc in top_k_docs)

        # === Prompt Template ===
        prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template="""
You are to generate a valid Python script using **only** the Manim and math libraries for Manim Community v0.19.
Output raw Python code only. Do not use Markdown formatting (no triple backticks). Do not include ```python or any code fences.

**Rules:**
- Output only raw Python code — no Markdown, no triple backticks.
- Do not include explanations, comments, or helper functions.
- Do not import any modules except `manim` and `math`.
- Use only variable names of 1–2 characters.
- Never use infinite loops.
- The animation must last at least 5 seconds.
- The script must end with a `self.play(...)` call.
- Assume it will be rendered directly using `manim`.

**Use this scaffold:**

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

        return InferenceResponse(result=response.content)

    async def generate_video_from_prompt(self, prompt: str) -> str:
        request = InferenceRequest(prompt=prompt)
        response = await self.run_inference(request)
        script = response.result
        video_path = render_manim_script(script)
        return video_path
