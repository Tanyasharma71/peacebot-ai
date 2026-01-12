import logging
import json
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from utils.request_id_context import get_request_id,set_request_id

SESSION_REQUEST_ID = set_request_id() 

class JsonFormatter(logging.Formatter):
    """Simple JSON formatter — only essential info (time, level, module, message)."""
    def format(self, record):
        log_data = {
            "session_id": getattr(record, "request_id", "-"),
            "time": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage()
            
        }
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


class RequestIdFilter(logging.Filter):
    """Injects the request_id into each log record."""
    def filter(self, record):
        record.request_id = SESSION_REQUEST_ID
        return True

def get_logger(name: str = "peacebot"):
    """Return a configured logger with structured log folder: logs/<year>/<month>/<day>/peacebot.log"""
    logger = logging.getLogger(name)
    if getattr(logger, "_configured", False):
        return logger

    logger.setLevel(logging.INFO)

    

    #  Folder structure: logs/YYYY/MonthName/DD
    now = datetime.now()
    year_folder = now.strftime("%Y")
    month_folder = now.strftime("%B")   # e.g., "November"
    day_folder = now.strftime("%d")

    log_dir = os.path.join("logs", year_folder, month_folder, day_folder)
    os.makedirs(log_dir, exist_ok=True)

    #  Log file path (rotates daily)
    log_file = os.path.join(log_dir, "peacebot.log")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())

    # File handler — rotates daily, keeps last 7 days
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=False
    )
    file_handler.setFormatter(JsonFormatter())

    logger.addFilter(RequestIdFilter())

    # Prevent duplicates
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    logger._configured = True

    return logger
