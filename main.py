
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from f1 import generate_manim_code
from f2 import render_manim_script
import os

app = FastAPI()

class Prompt(BaseModel):
    prompt: str

@app.post("/generate-video")
def generate_video(data: Prompt):
    try:
        # Step 1: Generate Manim Python script
        script = generate_manim_code(data.prompt)

        # Step 2: Render script into video
        video_path = render_manim_script(script)

        return {"status": "success", "video_path": video_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
