# """Custom exception handlers."""

# from fastapi import Request, HTTPException
# from fastapi.responses import JSONResponse
# from app.core.logger import logger


# class LLMServiceException(Exception):
#     """Base exception for LLM service."""
    
#     def __init__(self, message: str, status_code: int = 500):
#         self.message = message
#         self.status_code = status_code
#         super().__init__(self.message)


# class LLMProviderException(LLMServiceException):
#     """Exception for LLM provider errors."""
    
#     def __init__(self, message: str = "LLM provider error"):
#         super().__init__(message, status_code=503)


# class ValidationException(LLMServiceException):
#     """Exception for validation errors."""
    
#     def __init__(self, message: str = "Validation error"):
#         super().__init__(message, status_code=422)


# class RateLimitException(LLMServiceException):
#     """Exception for rate limiting."""
    
#     def __init__(self, message: str = "Rate limit exceeded"):
#         super().__init__(message, status_code=429)


# async def llm_service_exception_handler(request: Request, exc: LLMServiceException):
#     """Handle LLM service exceptions."""
#     logger.error(f"LLM Service Exception: {exc.message}")
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": {
#                 "type": type(exc).__name__,
#                 "message": exc.message,
#                 "status_code": exc.status_code
#             }
#         }
#     )


# async def general_exception_handler(request: Request, exc: Exception):
#     """Handle general exceptions."""
#     logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": {
#                 "type": "InternalServerError",
#                 "message": "An internal server error occurred",
#                 "status_code": 500
#             }
#         }
#     )


# async def http_exception_handler(request: Request, exc: HTTPException):
#     """Handle HTTP exceptions."""
#     logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": {
#                 "type": "HTTPException",
#                 "message": exc.detail,
#                 "status_code": exc.status_code
#             }
#         }
#     )
