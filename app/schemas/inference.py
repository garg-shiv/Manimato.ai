"""Inference schemas for request/response models."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class InferenceRequest(BaseModel):
    """Inference request model."""
    prompt: str
    chain_type: str = "simple"  # "simple", "analysis", "summary"
    parameters: Dict[str, Any] = {}
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class InferenceResponse(BaseModel):
    """Inference response model."""
    result: str
    chain_type: str
    usage: Optional[dict] = None
