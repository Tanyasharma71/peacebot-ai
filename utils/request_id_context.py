import uuid
import contextvars

_request_id_var = contextvars.ContextVar("request_id", default=None)

def set_request_id(request_id: str = None):
    """Create or set the request ID for this execution context."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    _request_id_var.set(request_id)
    return request_id

def get_request_id() -> str:
    """Retrieve current request ID if present."""
    return _request_id_var.get() or "-"

def clear_request_id():
    """Clear request ID when processing is done."""
    _request_id_var.set(None)
