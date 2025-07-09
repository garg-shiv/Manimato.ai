import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("request_logger")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        request.state.request_id = request_id
        try:
            response: Response = await call_next(request)
            duration = time.time() - start_time
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"in {duration:.3f}s"
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error {request_id}: {str(e)} "
                f"after {duration:.3f}s",
                exc_info=True
            )
            raise

def add_request_logger_middleware(app):
    app.add_middleware(RequestLoggingMiddleware)
