"""Helper utility functions."""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


def generate_uuid() -> str:
    """
    Generate and return a new UUID string using UUID version 4.
    	
    Returns:
    	str: A randomly generated UUID in string format.
    """
    return str(uuid.uuid4())


def get_current_timestamp() -> str:
    """Get current timestamp as ISO string."""
    return datetime.utcnow().isoformat()


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: Any = None) -> Optional[str]:
    """Safely dump object to JSON string."""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_error_message(error: Exception, include_type: bool = True) -> str:
    """Format error message for logging."""
    if include_type:
        return f"{type(error).__name__}: {str(error)}"
    return str(error)


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def is_valid_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
