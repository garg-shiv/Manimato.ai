"""
Simple Custom Exception System for Manimato.ai

A lightweight error handling system that makes debugging easier.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException


class ApiException(Exception):
    """
    A simple custom exception class that helps with debugging.
    
    Features:
    - Unique error ID for tracking
    - Timestamp for when error occurred  
    - Additional context for debugging
    - Easy conversion to HTTP responses
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "CUSTOM_ERROR",
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Create a custom error.
        
        Args:
            message: Error description for developers
            error_code: Short code to identify error type (e.g., "AUTH_FAILED") 
            status_code: HTTP status code for API responses
            context: Extra info for debugging (e.g., user_id, request_data)
        """
        super().__init__(message)
        self.error_id = str(uuid.uuid4())[:8]  # Short ID for easier tracking
        self.timestamp = datetime.utcnow()
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.context = context or {}
        
    def __str__(self) -> str:
        """String representation for logging."""
        return f"[{self.error_id}] {self.error_code}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }
    
    def to_http_response(self, include_details: bool = False) -> HTTPException:
        """
        Convert to FastAPI HTTP exception.
        
        Args:
            include_details: Whether to include debug info in response
        """
        detail: Dict[str, Any] = {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": "An error occurred. Please try again."
        }
        
        if include_details:
            detail["debug_message"] = self.message
            detail["context"] = self.context
            detail["timestamp"] = self.timestamp.isoformat()
        
        return HTTPException(status_code=self.status_code, detail=detail)


# Common error types for convenience
def auth_error(message: str = "Authentication failed", **context) -> ApiException:
    """Create an authentication error."""
    return ApiException(
        message=message,
        error_code="AUTH_FAILED", 
        status_code=401,
        context=context
    )


def not_found_error(resource: str, identifier: Optional[str] = None, **context) -> ApiException:
    """Create a 'not found' error."""
    msg = f"{resource} not found"
    if identifier:
        msg += f" (ID: {identifier})"
        context["identifier"] = identifier
    
    return ApiException(
        message=msg,
        error_code="NOT_FOUND",
        status_code=404,
        context={"resource": resource, **context}
    )


def validation_error(message: str, field: Optional[str] = None, **context) -> ApiException:
    """Create a validation error."""
    if field:
        context["field"] = field
    
    return ApiException(
        message=message,
        error_code="VALIDATION_ERROR",
        status_code=422,
        context=context
    )


def business_error(message: str, **context) -> ApiException:
    """Create a business logic error."""
    return ApiException(
        message=message,
        error_code="BUSINESS_ERROR",
        status_code=400,
        context=context
    )


def server_error(message: str = "Internal server error", **context) -> ApiException:
    """Create a server error."""
    return ApiException(
        message=message,
        error_code="SERVER_ERROR",
        status_code=500,
        context=context
    )
