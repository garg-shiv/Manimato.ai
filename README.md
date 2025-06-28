# 🧠 RAG-Powered Manim Video Generator (LangChain + FastAPI)

**Manimato.ai** is an AI-powered web app that translates natural language prompts into Manim animations using Retrieval-Augmented Generation (RAG), LLM-driven code synthesis, and real-time video rendering. It uses a vector database of 500+ indexed Manim examples and official docs to guide generation. Designed for cost-efficiency and high-quality output using open-source components.

- ✅ 90%+ generation accuracy  
- 💰 ~80% reduction in token usage via top-k semantic retrieval  
- ⚡ Real-time rendering using Manim  
- 🧠 Built with LangChain, FAISS, OpenRouter, FastAPI  

## 🔧 Setup

```bash
git clone https://github.com/your-username/manimato-ai
cd manimato-ai
pip install -r requirements.txt
uvicorn main:app --reload
```

📡 API Usage
POST /generate-video

Example request

```json
{
  "prompt": "Draw a triangle turning into a square"
}

```
Example response
```json
{
  "status": "success",
  "video_path": "generated/output_abcd1234.mp4"
}

```
## ⚙️ How It Works

- User submits a natural language prompt to the `/generate-video` endpoint.
- LangChain performs top-k retrieval from a FAISS index of 500+ Manim examples and official docs.
- Retrieved chunks are inserted into a Manim-specific prompt template.
- A language model (via OpenRouter) generates valid Manim-compatible Python code.
- The script is saved to a temporary file.
- Manim CLI is used to render it into a video via subprocess.
- The API responds with the path to the generated `.mp4`.

📁 Project Structure
```bash

├── main.py                         # FastAPI app
├── f1.py                           # LangChain + RAG + LLM code generation
├── f2.py                           # Manim video rendering logic
├── requirements.txt
├── cleaned_index_mapping.json      # Text chunks mapped to FAISS vector index
├── cleaned_manim_faiss.index       # FAISS vector store
├── render.yaml                     # Render deployment config
└── README.md

```
🚀 Deployment
You can deploy to Render using the included config:

```bash

# render.yaml is already configured
# Just push the repo and connect it to your Render account
```
Once deployed, send a POST request to /generate-video with your prompt and receive a fully rendered Manim video in return.
