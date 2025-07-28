"""
Manimato.ai Error Handler Package

Simple and effective error handling for better debugging.
"""

from .exceptions import (
    ApiException,
    auth_error,
    business_error,
    not_found_error,
    server_error,
    validation_error,
)
from error_handler.handler import add_error_handlers
from .logger import log_debug, log_error, log_info, log_warning

__all__ = [
    # Main error class
    "ApiException",
    # Convenience functions
    "auth_error",
    "business_error", 
    "not_found_error",
    "server_error",
    "validation_error",
    # Handler setup
    "add_error_handlers",
    # Logging functions
    "log_debug",
    "log_error", 
    "log_info",
    "log_warning",
]
