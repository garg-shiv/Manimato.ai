"""Inference API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_chain_manager
from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.chain_manager import ChainManager

router = APIRouter()


@router.post("/inference", response_model=InferenceResponse)
async def inference_endpoint(
    request: InferenceRequest, chain_manager: ChainManager = Depends(get_chain_manager)
):
    """Handle inference requests."""
    try:
        response = await chain_manager.run_inference(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
