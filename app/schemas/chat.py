"""Chat schemas for request/response models."""

from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[ChatMessage]
    conversation_id: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    conversation_id: Optional[str] = None
    usage: Optional[dict] = None
