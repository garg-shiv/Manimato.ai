"""API v1 router configuration."""

from fastapi import APIRouter
from app.api.v1.endpoints import chat, inference

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(inference.router, prefix="/inference", tags=["inference"])
