import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "peacebot.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter — only essential info (time, level, module, message)."""
    def format(self, record):
        log_data = {
            "time": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }

        # Optional: include exception info if exists
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str = "peacebot"):
    """Return a configured logger with clean output."""
    logger = logging.getLogger(name)

    if getattr(logger, "_configured", False):
        return logger  # Avoid duplicate handlers

    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())

    # Rotating file handler
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(JsonFormatter())

    # Clear previous handlers (avoid duplication)
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False
    logger._configured = True

    return logger
