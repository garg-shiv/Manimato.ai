import os

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_chain_manager
from app.schemas.inference import InferenceRequest
from app.services.chain_manager import ChainManager

router = APIRouter()


@router.post("/generate-video")
async def generate_video(
    data: InferenceRequest, chain_manager: ChainManager = Depends(get_chain_manager)
):
    try:
        # Step 1 & 2: Generate script + render video
        result = await chain_manager.generate_video_from_prompt(data.prompt)

        # Step 3: Return relative URL
        return {"status": "success", "video_url": f"/videos/{os.path.basename(result)}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))