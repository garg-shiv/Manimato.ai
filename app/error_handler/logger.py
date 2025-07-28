"""
Simple Logging Helper for Manimato.ai

Easy-to-use logging functions that work well with custom errors.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import ApiException


# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("manimato")


def setup_file_logging():
    """Setup file logging in addition to console logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create file handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)


def log_error(
    error: ApiException,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None
):
    """
    Log a custom error with full context.
    
    Args:
        error: The CustomError instance
        request_id: Optional request ID for tracking
        user_id: Optional user ID for tracking  
        extra_context: Additional context to log
    """
    context = {
        **error.to_dict(),
        **(extra_context or {})
    }
    
    if request_id:
        context["request_id"] = request_id
    if user_id:
        context["user_id"] = user_id
    
    logger.error(f"Custom Error: {error}", extra={"context": json.dumps(context)})


def log_info(message: str, **context):
    """Log info message with optional context."""
    if context:
        logger.info(f"{message} | Context: {json.dumps(context)}")
    else:
        logger.info(message)


def log_warning(message: str, **context):
    """Log warning message with optional context."""
    if context:
        logger.warning(f"{message} | Context: {json.dumps(context)}")
    else:
        logger.warning(message)


def log_debug(message: str, **context):
    """Log debug message with optional context."""
    if context:
        logger.debug(f"{message} | Context: {json.dumps(context)}")
    else:
        logger.debug(message)


# Initialize file logging
setup_file_logging()
