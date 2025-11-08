"""Gratitude logging module for Peacebot.

This module provides functionality to log gratitude entries both interactively
(CLI) and non-interactively (programmatic).
"""

import json
import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__))) 
from utils.logger_config import get_logger
from typing import List

# Configure logging
logger = get_logger(__name__)

# Constants
DATA_FILE = "gratitude_log.json"
MAX_GRATITUDE_ITEMS = 3


def log_gratitude() -> str:
    """Interactive gratitude logging for CLI usage.
    
    Prompts the user to enter 3 things they're grateful for and saves them
    to the gratitude log file.
    
    Returns:
        Success message string
    """
    logger.info("Starting interactive gratitude logging session")
    print("Let's do a quick gratitude practice 🌈")
    gratitude_list = []
    
    for i in range(1, MAX_GRATITUDE_ITEMS + 1):
        try:
            item = input(f"Thing {i} you're grateful for: ").strip()
            if item:
                gratitude_list.append(item)
            else:
                logger.warning(f"Empty input for gratitude item {i}")
        except (KeyboardInterrupt, EOFError):
            logger.info("Gratitude logging interrupted by user")
            if gratitude_list:
                break
            return "Gratitude practice cancelled."

    if not gratitude_list:
        logger.info("No gratitude items entered during session")
        return "No gratitude items entered."

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "gratitude": gratitude_list,
        "source": "interactive"
    }
    
    try:
        _save_gratitude_entry(entry)
        logger.info(f"Saved {len(gratitude_list)} gratitude items")
        return "Your gratitude list is saved 💛 Take a moment to feel the warmth."
    except Exception as e:
        logger.error(f"Error saving gratitude entry: {str(e)}")
        return "Sorry, there was an error saving your gratitude list."


def log_gratitude_noninteractive(items: List[str]) -> str:
    """Save a provided list of 1-3 gratitude items in non-interactive contexts.

    Parameters
    ----------
    items : list[str]
        One to three short gratitude statements.
        
    Returns
    -------
    str
        Success message
        
    Raises
    ------
    ValueError
        If items is not a valid list or contains no valid entries
    """
    if not items or not isinstance(items, list):
        raise ValueError("items must be a non-empty list of strings")

    # Clean and validate items
    trimmed = [str(x).strip() for x in items if str(x).strip()]
    
    if not trimmed:
        raise ValueError("no valid items provided")
    
    if len(trimmed) > MAX_GRATITUDE_ITEMS:
        logger.warning(f"Trimming gratitude items from {len(trimmed)} to {MAX_GRATITUDE_ITEMS}")
        trimmed = trimmed[:MAX_GRATITUDE_ITEMS]

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "gratitude": trimmed,
        "source": "noninteractive",
    }
    
    try:
        _save_gratitude_entry(entry)
        logger.info(f"Saved {len(trimmed)} gratitude items (noninteractive)")
        return "Saved your gratitude list."
    except Exception as e:
        logger.error(f"Error saving gratitude entry: {str(e)}")
        raise


def _save_gratitude_entry(entry: dict) -> None:
    """Save a gratitude entry to the data file.
    
    Parameters
    ----------
    entry : dict
        Gratitude entry containing timestamp, gratitude list, and source
        
    Raises
    ------
    Exception
        If there's an error reading or writing the file
    """
    data = []
    
    # Read existing data if file exists
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.warning("Gratitude data file is not a list, resetting")
                    data = []
        except json.JSONDecodeError:
            logger.error("Gratitude data file is corrupted, creating new file")
            data = []
        except Exception as e:
            logger.error(f"Error reading gratitude file: {str(e)}")
            raise
    
    # Append new entry
    data.append(entry)
    
    # Write back to file
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing gratitude file: {str(e)}")
        raise


def get_gratitude_history(limit: int = 10) -> List[dict]:
    """Retrieve recent gratitude entries.
    
    Parameters
    ----------
    limit : int, optional
        Maximum number of entries to return (default: 10)
        
    Returns
    -------
    list[dict]
        List of gratitude entries, most recent first
    """
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.warning("Gratitude data file is not a list")
                return []
            # Return most recent entries first
            return data[-limit:][::-1]
    except json.JSONDecodeError:
        logger.error("Gratitude data file is corrupted")
        return []
    except Exception as e:
        logger.error(f"Error reading gratitude history: {str(e)}")
        return []
