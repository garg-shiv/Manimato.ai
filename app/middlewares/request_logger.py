# """Request logging middleware."""

# import time
# import uuid
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
# from starlette.responses import Response
# from app.core.logger import logger


# class RequestLoggingMiddleware(BaseHTTPMiddleware):
#     """Middleware for logging HTTP requests and responses."""

#     async def dispatch(self, request: Request, call_next):
#         """Process request and log details."""
#         # Generate request ID
#         request_id = str(uuid.uuid4())

#         # Start timer
#         start_time = time.time()

#         # Log incoming request
#         logger.info(
#             f"Request {request_id}: {request.method} {request.url.path} "
#             f"from {request.client.host if request.client else 'unknown'}"
#         )

#         # Add request ID to state
#         request.state.request_id = request_id

#         try:
#             # Process request
#             response: Response = await call_next(request)

#             # Calculate duration
#             duration = time.time() - start_time

#             # Log response
#             logger.info(
#                 f"Response {request_id}: {response.status_code} "
#                 f"in {duration:.3f}s"
#             )

#             # Add request ID to response headers
#             response.headers["X-Request-ID"] = request_id

#             return response

#         except Exception as e:
#             # Calculate duration
#             duration = time.time() - start_time

#             # Log error
#             logger.error(
#                 f"Error {request_id}: {str(e)} "
#                 f"after {duration:.3f}s",
#                 exc_info=True
#             )

#             raise
