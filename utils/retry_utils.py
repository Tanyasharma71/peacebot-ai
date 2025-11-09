# utils/retry_utils.py
import time
import functools
from utils.logger_config import get_logger

logger = get_logger("peacebot.retry")

def retry(max_retries=5, base_delay=1, exceptions=(Exception,)):
    """Generic retry decorator with exponential backoff and structured logging."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < max_retries:
                        logger.warning(
                            f"Retry {attempt}/{max_retries} for {func.__name__} after error: {e}",
                            extra={"function": func.__name__, "attempt": attempt, "delay": delay}
                        )
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        logger.error(
                            f"All {max_retries} retries failed for {func.__name__}",
                            extra={"function": func.__name__, "error": str(e)}
                        )
                        raise
        return wrapper
    return decorator
