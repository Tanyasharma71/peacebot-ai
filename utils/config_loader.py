import os
import configparser

# Determine config path relative to project root
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config" ,"config.ini")

config = configparser.ConfigParser()
config.read(CONFIG_PATH)


def get(section: str, key: str, fallback=None):
    """Get a config value as string."""
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def getint(section: str, key: str, fallback=None):
    """Get a config value as int."""
    try:
        return config.getint(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return fallback


def getboolean(section: str, key: str, fallback=None):
    """Get a config value as bool."""
    try:
        return config.getboolean(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return fallback
