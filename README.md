# 🧠 RAG-Powered Manim Video Generator (LangChain + FastAPI)

This project takes a prompt and generates a Manim animation using LangChain and vector-based retrieval (RAG), then renders it to a video.

### 📦 Setup
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### 🌐 Endpoint
- `POST /generate-video`
```json
{
  "prompt": "Draw a triangle turning into a square"
}
```

### 📁 Structure
- `f1.py`: RAG + LLM to generate Python script
- `f2.py`: Renders the script using Manim
- `main.py`: FastAPI app

### 🚀 Deployment
Use `render.yaml` to deploy to [Render](https://render.com).