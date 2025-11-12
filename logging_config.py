"""Logging configuration for the application."""

import logging
import logging.config
import os

LOGLEVEL = None

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "log/agent.log",
            "maxBytes": 10_000_000,
            "backupCount": 5,
            "formatter": "standard",
            "level": LOGLEVEL
        }
    },
    "root": {
        "handlers": ["file"],
        "level": LOGLEVEL
    },
    "loggers": {
        "LiteLLM": {
            "handlers": ["file"],
            "level": LOGLEVEL,
            "propagate": False
        },
        "LiteLLM Router": {
            "handlers": ["file"],
            "level": LOGLEVEL,
            "propagate": False
        },
        "LiteLLM Proxy": {
            "handlers": ["file"],
            "level": LOGLEVEL,
            "propagate": False
        }
    }
}

def setup_logging():
    """Set up logging configuration."""
    global LOGLEVEL
    LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    # Remove all handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # Remove all handlers from LiteLLM loggers
    for logger_name in ["LiteLLM", "LiteLLM Router", "LiteLLM Proxy"]:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    # Set up logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger().setLevel(LOGLEVEL)
    for logger_name in ["root", "LiteLLM", "LiteLLM Router", "LiteLLM Proxy"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(LOGLEVEL)
        logger.propagate = False
