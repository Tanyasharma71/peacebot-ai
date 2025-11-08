import json
import os
import datetime
import logging
from typing import List

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "gratitude_log.json")

def log_gratitude_noninteractive(items: List[str]) -> str:
    """Save gratitude list."""
    if not items:
        raise ValueError("Empty gratitude list")
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "gratitude": items[:3],
        "source": "noninteractive"
    }
    try:
        data = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE) as f:
                data = json.load(f)
        data.append(entry)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Gratitude logged successfully")
        return "Gratitude logged."
    except Exception as e:
        logger.error(f"Error logging gratitude: {e}")
        raise
