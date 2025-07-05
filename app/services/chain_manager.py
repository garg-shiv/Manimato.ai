import json
import os

import faiss
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.render_service import render_manim_script

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or "dummy"
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

class ChainManager:
    async def run_inference(self, request: InferenceRequest) -> InferenceResponse:
        query = request.prompt

        # === Load LLM ===

        llm = ChatOpenAI(
        model="meta-llama/llama-4-maverick:free",
        temperature=0.2,
    )


        # === Load FAISS Index and Mapping ===
        base_dir = os.path.dirname(os.path.abspath(__file__))
        index_path = os.path.join(base_dir, "..", "..", "cleaned_manim_faiss.index")
        mapping_path = os.path.join(base_dir, "..", "..", "cleaned_index_mapping.json")

        index = faiss.read_index(index_path)
        with open(mapping_path, "r", encoding="utf-8") as f:
            doc_data = json.load(f)

        documents = [Document(page_content=d["content"]) for d in doc_data]
        doc_ids = [str(i) for i in range(len(documents))]
        docstore = InMemoryDocstore(dict(zip(doc_ids, documents)))
        index_to_docstore_id = {i: doc_ids[i] for i in range(len(doc_ids))}

        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        vectorstore = FAISS(
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
            embedding_function=embedding_model
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

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
        """
        )

        # === QA Chain ===
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            input_key="query",
            chain_type_kwargs={"prompt": prompt_template}
        )

        response = qa_chain({"query": query})
        return InferenceResponse(result=response["result"])

    async def generate_video_from_prompt(self, prompt: str) -> str:
        # Use your own run_inference logic
        request = InferenceRequest(prompt=prompt)
        response = await self.run_inference(request)

        script = response.result
        video_path = render_manim_script(script)
        return video_path
