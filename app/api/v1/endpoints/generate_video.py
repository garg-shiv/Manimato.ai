import os
from fastapi import APIRouter, HTTPException
from schemas.inference import Prompt
from services.chain_manager import generate_manim_code
from services.render_service import render_manim_script

router = APIRouter()

@router.post("/generate-video")
def generate_video(data: Prompt):
    try:
        # Step 1: Generate Manim Python code from prompt
        script = generate_manim_code(data.prompt)

        # Step 2: Render the script into a video
        video_path = render_manim_script(script)
        filename = os.path.basename(video_path)

        # Step 3: Return the relative URL to the client
        return {
            "status": "success",
            "video_url": f"/videos/{filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
