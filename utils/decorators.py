import functools
import traceback
from typing import Any, Callable, Optional, Dict


from utils.logger_config import get_logger
from utils.request_id_context import get_request_id

logger = get_logger(__name__)

def safe_execution(fallback_value: Optional[Any] = None, reraise: bool = True):
    """
    Decorator that centralizes exception handling and logging.

    Parameters:
    - fallback_value: value to return if an exception happens and reraise is False.
    - reraise: if True, decorator re-raises the exception after logging; if False, returns fallback_value.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # Build error payload
                rid = None
                try:
                    rid = get_request_id()
                except Exception:
                    # To not let context reading break logging
                    rid = None

                tb = traceback.format_exc()

                # Structured log entry (the logger is the one from logger_config)
                logger.error(
                    {
                        "error": str(exc),
                        "traceback": tb,
                        "function": getattr(func, "__qualname__", func.__name__),
                        "request_id": rid,
                    }
                )

                # Optionally re-raise (dev) or swallow (prod)
                if reraise:
                    raise
                return fallback_value
        return wrapper
    return decorator
