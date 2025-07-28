"""
Error Handler for FastAPI Integration

Provides middleware and exception handlers for the FastAPI application.
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import config

from .exceptions import ApiException
from .logger import log_error, log_warning


async def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
    """Handle custom errors and return appropriate JSON response."""
    
    # Log the error with request context
    log_error(
        error=exc,
        request_id=getattr(request.state, 'request_id', None),
        user_id=getattr(request.state, 'user_id', None),
        extra_context={
            "url": str(request.url),
            "method": request.method,
            "client_host": request.client.host if request.client else None
        }
    )
    
    # Return user-friendly response (set include_details=True for development)
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_http_response(include_details=config.ENV == "dev").detail
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors."""
    
    # Create a custom error for better tracking
    custom_exc = ApiException(
        message=f"Validation failed: {exc.errors()}",
        error_code="VALIDATION_ERROR",
        status_code=422,
        context={"validation_errors": exc.errors()}
    )
    
    log_warning(
        f"Validation error on {request.method} {request.url}",
        validation_errors=exc.errors(),
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error_id": custom_exc.error_id,
            "error_code": "VALIDATION_ERROR", 
            "message": "Invalid input data",
            "details": exc.errors()
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    
    log_warning(
        f"HTTP {exc.status_code} on {request.method} {request.url}",
        status_code=exc.status_code,
        detail=exc.detail,
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail
        }
    )


def add_error_handlers(app):
    """Add all error handlers to the FastAPI app."""
    
    app.add_exception_handler(ApiException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
