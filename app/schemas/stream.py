from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


class StreamEvent(BaseModel):
    """Schema for streaming events"""

    type: Literal[
        "message_created",
        "code_chunk",
        "ai_completed",
        "error",
        "file_saved",
        "cloud_uploaded",
        "completed",
    ]
    data: Optional[str] = None
    message_id: Optional[int] = None

    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }


class PromptRequest(BaseModel):
    """Schema for prompt requests"""

    chat_id: int
    prompt: str


class MessageResponse(BaseModel):
    """Schema for message creation response"""

    message_id: int
    status: str


class MessageType(Enum):
    """Message types for streaming responses"""

    CONTENT = "content"
    ERROR = "error"
    END = "end"
    START = "start"  # Optional: for stream initialization
    METADATA = "metadata"  # Optional: for additional info


class StreamMarkers:
    """Internal stream markers"""

    STREAM_END = "__STREAM_END__"
    STREAM_START = "__STREAM_START__"
    STREAM_ERROR = "__STREAM_ERROR__"


class ErrorMessages:
    """User-friendly error messages"""

    GENERAL_ERROR = "I'm sorry, I encountered an issue while processing your request. Please try again."
    TIMEOUT_ERROR = "The request timed out. Please try again."
    RATE_LIMIT_ERROR = "Too many requests. Please wait a moment and try again."
    INVALID_INPUT = (
        "I'm having trouble understanding your request. Please try rephrasing."
    )
    SYSTEM_ERROR = (
        "I'm currently unable to process your request. Please try again later."
    )
