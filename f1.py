
import os
import json
import faiss
import numpy as np
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI

load_dotenv()

def generate_manim_code(query: str) -> str:
    # === Load LLM ===
    llm = ChatOpenAI(
        model_name="meta-llama/llama-4-maverick:free",
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"
    )

    # === Load FAISS Index and Mapping ===
    index = faiss.read_index("cleaned_manim_faiss.index")
    with open("cleaned_index_mapping.json", "r", encoding="utf-8") as f:
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

    # === Prompt Template ===
    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template=""" 
Write a Manim animation in Python using only the Manim and math libraries. Do not use any other libraries or imports.
- Output only a single, complete code block.
- Do NOT include explanations, comments, or helper functions.
- Make the video at least 5 seconds long.
- Never use infinite loops.
- Use variable names with a max length of 2.
- Always end with a self.play(...) call to animate the result.
- Do not import any other libraries.
- Use only valid syntax for Manim Community v0.19.

Use this code scaffold:

from manim import *
from math import *

class GenScene(Scene):
    def construct(self):
        # Write here

User prompt:
{question}

Here are a few relevant examples:
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
    return response["result"]
