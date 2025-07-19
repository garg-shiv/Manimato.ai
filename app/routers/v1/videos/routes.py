import os

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_chain_manager
from app.schemas.inference import InferenceRequest
from app.services.chain_manager import ChainManager

router = APIRouter(tags=["videos"])


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


# @router.post("/stream-code")
# async def stream_code(
#     data: InferenceRequest, chain_manager: ChainManager = Depends(get_chain_manager)
# ):
#     try:
#         stream = chain_manager.run_inference_stream(data)
#         return StreamingResponse(stream, media_type="text/plain")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
