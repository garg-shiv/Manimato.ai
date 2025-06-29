"""Chat API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.deps import get_chat_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Handle chat requests."""
    try:
        response = await chat_service.process_chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
