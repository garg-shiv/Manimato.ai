#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import faiss
# import json
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv
# load_dotenv()

# model = SentenceTransformer('all-MiniLM-L6-v2')

# with open('cleaned_manim_examples.json') as f:
#     data = json.load(f)

# texts = [item['title'] + "\n" + item['content'] for item in data]

# embeddings = model.encode(texts)  # This returns a list of vectors

# # Convert to NumPy float32 array
# embedding_array = np.array(embeddings).astype("float32")

# # Create FAISS index
# index = faiss.IndexFlatL2(embedding_array.shape[1])  # 384 for MiniLM

# # Add vectors
# index.add(embedding_array)


# faiss.write_index(index, "cleaned_manim_faiss.index")

# # Save mapping separately
# with open("cleaned_index_mapping.json", "w") as f:
#     json.dump(data, f)

# print("FAISS index and mapping saved successfully.")


# In[ ]:


import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

# === Load embedding model ===
model = SentenceTransformer('all-MiniLM-L6-v2')

# === Load structured Manim documentation ===
with open(r"C:\Users\Harish Ramaswamy\OneDrive\Desktop\rag-core\manim_documentation.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

# === Prepare inputs ===
texts = [doc["name"] + "\n" + doc["code"] for doc in docs]
embeddings = model.encode(texts, show_progress_bar=True)
embedding_array = np.array(embeddings).astype("float32")

# === Build FAISS index ===
index = faiss.IndexFlatL2(embedding_array.shape[1])  # 384 dims
index.add(embedding_array)

# === Save index + mapping ===
faiss.write_index(index, "cleaned_manim_doc_faiss.index")

with open("cleaned_doc_index_mapping.json", "w", encoding="utf-8") as f:
    json.dump(docs, f)

print("✅ Manim documentation FAISS index built and saved.")


# In[ ]:


# from langchain.prompts import PromptTemplate
# from langchain_core.documents import Document
# from langchain.chains import RetrievalQA
# from langchain_community.vectorstores import FAISS
# from langchain.docstore.in_memory import InMemoryDocstore
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.chat_models import ChatOpenAI  # ✅ NEW: OpenRouter-compatible
# from dotenv import load_dotenv
# import numpy as np
# import faiss
# import os
# import json

# # === 1. Load env and OpenRouter API ===
# load_dotenv()

# llm = ChatOpenAI(
#     model_name="meta-llama/llama-4-maverick:free",  # ✅ Free LLM that follows code style
#     temperature=0,
#     openai_api_key=os.getenv("OPENROUTER_API_KEY"),
#     openai_api_base="https://openrouter.ai/api/v1",
# )

# # === 2. Load FAISS index and docs ===
# index = faiss.read_index("cleaned_manim_faiss.index")
# with open("cleaned_index_mapping.json", "r", encoding="utf-8") as f:
#     doc_data = json.load(f)
# documents = [Document(page_content=d["content"]) for d in doc_data]

# doc_ids = [str(i) for i in range(len(documents))]
# docstore = InMemoryDocstore(dict(zip(doc_ids, documents)))
# index_to_docstore_id = {i: doc_ids[i] for i in range(len(doc_ids))}

# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# vectorstore = FAISS(
#     index=index,
#     docstore=docstore,
#     index_to_docstore_id=index_to_docstore_id,
#     embedding_function=embedding_model
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# # === 3. Prompt Template ===
# prompt_template = PromptTemplate(
#     input_variables=["question", "context"],
#     template="""
# Write a Manim animation in Python using only the Manim and math libraries. Do not use any other libraries or imports. Do not use Latex dependent functions.
# - Output only a single, complete code block.
# - Do NOT include explanations, comments, or helper functions.
# - Make the video at least 5 seconds long.
# - Never use infinite loops.
# - Use variable names with a max length of 2.
# - Always end with a self.play(...) call to animate the result.
# - Do not import any other libraries.
# - Use only valid syntax for Manim Community v0.19.

# Use this code scaffold:

# from manim import *
# from math import *

# class GenScene(Scene):
#     def construct(self):
#         # Write here

# User prompt:
# {question}

# Here are a few relevant examples:
# {context}
# """
# )

# # === 4. RetrievalQA Chain ===
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     retriever=retriever,
#     chain_type="stuff",
#     input_key="query",
#     chain_type_kwargs={"prompt": prompt_template}
# )

# # === 5. Run the Chain ===
# if __name__ == "__main__":
#     query = "Draw a circle converting into a square while rolling on the ground."

#     docs = retriever.get_relevant_documents(query)
#     for i, d in enumerate(docs):
#         print(f"\n--- Retrieved Example {i+1} ---\n{d.page_content.strip()}\n")

#     response = qa_chain({"query": query})

#     print("\n=== Generated Manim Code ===\n")
#     print(response["result"])


# In[ ]:


from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import faiss
import os
import json
import numpy as np

# === 1. Load Env and LLM ===
load_dotenv()

llm = ChatOpenAI(
    model_name="meta-llama/llama-4-maverick:free",
    temperature=0,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# === 2. Load Example FAISS ===
example_index = faiss.read_index("cleaned_manim_faiss.index")
with open("cleaned_index_mapping.json", "r", encoding="utf-8") as f:
    example_data = json.load(f)
example_docs = [Document(page_content=d["content"]) for d in example_data]
example_ids = [str(i) for i in range(len(example_docs))]
example_docstore = InMemoryDocstore(dict(zip(example_ids, example_docs)))
example_index_to_id = {i: example_ids[i] for i in range(len(example_ids))}

example_vectorstore = FAISS(
    index=example_index,
    docstore=example_docstore,
    index_to_docstore_id=example_index_to_id,
    embedding_function=embedding_model,
)

# === 3. Load Doc FAISS ===
doc_index = faiss.read_index("cleaned_manim_doc_faiss.index")
with open("cleaned_doc_index_mapping.json", "r", encoding="utf-8") as f:
    doc_data = json.load(f)
doc_docs = [Document(page_content=d["code"]) for d in doc_data]
doc_ids = [str(i) for i in range(len(doc_docs))]
doc_docstore = InMemoryDocstore(dict(zip(doc_ids, doc_docs)))
doc_index_to_id = {i: doc_ids[i] for i in range(len(doc_ids))}

doc_vectorstore = FAISS(
    index=doc_index,
    docstore=doc_docstore,
    index_to_docstore_id=doc_index_to_id,
    embedding_function=embedding_model,
)

# === 3.5. Turn VectorStores into Retrievers ===
example_retriever = example_vectorstore.as_retriever(search_kwargs={"k": 10})
doc_retriever = doc_vectorstore.as_retriever(search_kwargs={"k": 10})


# === 4. Prompt Template ===
prompt_template = PromptTemplate(
    input_variables=["question", "example_context", "doc_context"],
    template="""
Write a Manim animation in Python using only the Manim and math libraries. Do not use any other libraries or imports. Do not use Latex dependent functions.
- Output only a single, complete code block.
- Do NOT include explanations, comments, or helper functions.
- Make the video as long as required.
- Never use infinite loops.
- Use variable names with a max length of 2.
- Always end with a self.play(...) call to animate the result.
- Do not import any other libraries.
- Do not use any functions that are not part of Manim Community v0.19. 
- Use only those functions that are defined in the Manim documentation and the examples ONLY.

Use this code scaffold:

from manim import *
from math import *

class GenScene(Scene):
    def construct(self):
        # Write here

User prompt:
{question}

Relevant Manim animation examples:
{example_context}

Relevant Manim function or class definitions:
{doc_context}
"""
)

# === 5. Unified Manual Chain (Custom Retrieval + LLM) ===
def hybrid_query_pipeline(query, k=10):
    # 5 examples + 3 doc matches
    example_hits = example_retriever.get_relevant_documents(query)
    doc_hits = doc_retriever.get_relevant_documents(query)


    example_context = "\n\n".join([d.page_content for d in example_hits])
    doc_context = "\n\n".join([d.page_content for d in doc_hits])

    full_prompt = prompt_template.format(
        question=query,
        example_context=example_context,
        doc_context=doc_context
    )



    response = llm([HumanMessage(content=full_prompt)])
    return response, example_hits, doc_hits

# === 6. Run the Chain ===
if __name__ == "__main__":
    query = "Convert a rolling circle into a square."

    response, examples, docs = hybrid_query_pipeline(query)

    print("\n--- Retrieved Examples ---")
    for i, d in enumerate(examples):
        print(f"\nExample {i+1}:\n{d.page_content.strip()}")

    print("\n--- Retrieved Docs ---")
    for i, d in enumerate(docs):
        print(f"\nDoc {i+1}:\n{d.page_content.strip()}")

    print("\n=== Final Generated Manim Code ===\n")
    print(response)


# In[30]:


# import os
# import re
# import subprocess

# # === Settings ===
# output_dir = "generated"
# media_dir = os.path.join(output_dir, "media")
# script_path = os.path.join(output_dir, "gen_scene.py")
# scene_name = "GenScene"  # must match class name in the generated code

# # === Step 0: Ensure output directory exists ===
# os.makedirs(output_dir, exist_ok=True)
# print(response)
# # === Step 1: Extract model output ===
# code_raw = response["content"]

# # === Step 2: Strip code fences (```python) if present ===
# code_clean = re.sub(r"^```python|```$", "", code_raw.strip(), flags=re.MULTILINE).strip()

# # === Step 3: Safety check ===
# if not code_clean or scene_name not in code_clean:
#     raise ValueError(f"Generated code is invalid or missing the scene class: {scene_name}")
# print(code_clean)



# In[46]:


import os
import re
import subprocess
from langchain_core.messages import AIMessage

# === Settings ===
output_dir = "generated"
media_dir = os.path.join(output_dir, "media")
script_path = os.path.join(output_dir, "gen_scene.py")
scene_name = "GenScene"  # Must match the class name in LLM output

# === Ensure output directory exists ===
os.makedirs(output_dir, exist_ok=True)

# === Extract and clean LLM output ===
if isinstance(response, AIMessage):
    code_raw = response.content
elif isinstance(response, dict) and "content" in response:
    code_raw = response["content"]
elif isinstance(response, str):
    code_raw = response
else:
    raise ValueError("Unsupported response format from LLM")

# === Clean out triple backticks + optional python tag ===
code_clean = re.sub(r"^```(?:python)?\s*|```$", "", code_raw.strip(), flags=re.MULTILINE).strip()

# === Safety check for scene name ===
if not code_clean or scene_name not in code_clean:
    raise ValueError(f"Generated code is invalid or missing the scene class: {scene_name}")

# === Optional: Print to verify ===
print("\n=== Final Cleaned Code ===\n")
print(code_clean)

# === Write to .py file ===
with open(script_path, "w", encoding="utf-8") as f:
    f.write(code_clean)


# In[47]:


# === Step 4: Save to a .py file ===
with open(script_path, "w", encoding="utf-8") as f:
    f.write(code_clean)

# === Step 5: Render with Manim CLI ===
print(f"🛠️ Rendering scene '{scene_name}' from '{script_path}'...\n")
result = subprocess.run([
    "manim",
    "-pql",
    script_path,
    scene_name,
    "--media_dir", media_dir
], capture_output=True, text=True, encoding="utf-8", errors="replace")


# === Step 6: Show results ===
if result.returncode == 0:
    print("✅ Render complete.")
    output_video = os.path.join(media_dir, "videos", "gen_scene", "480p15", f"{scene_name}.mp4")
    if os.path.exists(output_video):
        print(f"🎬 Video saved at: {output_video}")
    else:
        print("⚠️ Render succeeded, but video file not found.")
else:
    print("❌ Render failed!")
    print("=== STDOUT ===\n", result.stdout)
    print("=== STDERR ===\n", result.stderr)


# In[33]:


# from manim import *
# from math import *

# class GenScene(Scene):
#     def construct(self):
#         ax = Axes(x_range=[-5, 5], y_range=[-1.5, 1.5])
#         gr = ax.plot(lambda x: sin(x))
#         dt = Dot().move_to(ax.c2p(-5, sin(-5)))
#         self.add(ax, gr, dt)
#         self.play(dt.animate.move_along_path(gr, rate_func=linear), run_time=5)


# In[34]:


# import json
# import re
# from ast import parse

# def upgrade_code(content):
#     # Replace get_graph → plot
#     content = re.sub(r'(\w+)\.get_graph', r'\1.plot', content)

#     # Replace input_to_graph_point(...) → c2p(...)
#     content = re.sub(r'(\w+)\.input_to_graph_point\((.*?)\)', r'\1.c2p(\2)', content)

#     # Replace .move_along_path(...) → use MoveAlongPath
#     content = re.sub(
#         r'(\w+)\.animate\.move_along_path\((.*?),\s*rate_func=(.*?)\)',
#         r'MoveAlongPath(\1, \2, rate_func=\3)',
#         content
#     )

#     # Fix Dot(..., color=...) → Dot(...).set_color(...)
#     content = re.sub(
#         r'Dot\((.*?)color\s*=\s*(\w+)\)',
#         r'Dot(\1).set_color(\2)',
#         content
#     )

#     # Fix Line(..., color=...) → Line(...).set_color(...)
#     content = re.sub(
#         r'Line\((.*?)color\s*=\s*(\w+)\)',
#         r'Line(\1).set_color(\2)',
#         content
#     )

#     # Fix 2D move_to coords: move_to((x, y)) → move_to([x, y, 0])
#     content = re.sub(r'move_to\(\(\s*([^\s,]+)\s*,\s*([^)]+)\)\)', r'move_to([\1, \2, 0])', content)

#     # Normalize class name
#     content = re.sub(r"class\s+MyScene", "class GenScene", content)

#     # Add from math import * if math funcs are used but not already imported
#     if "sin(" in content and "from math import" not in content:
#         content = content.replace("from manim import *", "from manim import *\nfrom math import *")

#     return content

# def clean_and_upgrade_manim_json(json_path, output_path):
#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     seen = set()
#     upgraded = []

#     for entry in data:
#         content = entry["content"].strip()
#         content = upgrade_code(content)

#         norm = re.sub(r"\s+", "", content)
#         if norm in seen:
#             continue
#         seen.add(norm)

#         # Check syntax (optional)
#         try:
#             parse(content)
#         except SyntaxError:
#             continue

#         upgraded.append({
#             "title": entry["title"],
#             "content": content
#         })

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(upgraded, f, indent=2)

#     print(f"✅ Upgraded and saved {len(upgraded)} examples (from {len(data)}) → {output_path}")

# # Run this
# clean_and_upgrade_manim_json("manim_examples.json", "cleaned_manim_examples.json")

