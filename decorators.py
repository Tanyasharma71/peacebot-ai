import functools
import traceback
from utils.logger_config import get_logger
from utils.request_id_context import get_request_id  # <-- we’ll create this if not yet

logger = get_logger(__name__)

def safe_execution(fallback_value=None, reraise=True):
    """
    Decorator that wraps a function to centrally log all exceptions with traceback
    and request metadata (e.g., request_id).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                rid = None
                try:
                    rid = get_request_id()
                except Exception:
                    pass
                tb = traceback.format_exc()
                logger.error({
                    "error": str(e),
                    "traceback": tb,
                    "function": func.__name__,
                    "request_id": rid,
                })
                if reraise:
                    raise
                return fallback_value
        return wrapper
    return decorator
