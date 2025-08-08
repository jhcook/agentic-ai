import logging
import logging.config
import os

LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        # "console": {
        #     "class": "logging.StreamHandler",
        #     "formatter": "standard",
        #     "level": LOGLEVEL
        # },
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
        "handlers": ["file"], #["console", "file"],
        "level": LOGLEVEL
    }
    # "loggers": {
    #     "my_module": {
    #         "handlers": ["file"], #["console"],
    #         "level": LOGLEVEL,
    #         "propagate": False
    #     }
    # }
}

def setup_logging():
    """
    Set up application-wide logging configuration.

    This function creates the log directory if it does not exist, applies the logging configuration
    defined in LOGGING_CONFIG, and adjusts the logging behavior for the 'LiteLLM' logger to suppress
    less important logs.

    Logging configuration details:
      - Logs are written to 'log/agent.log' with rotation (max 10MB, 5 backups).
      - Log format includes timestamp, logger name, level, and message.
      - Log level is controlled by the LOGLEVEL environment variable (default: INFO).
      - Optionally supports JSON formatting (commented out by default).
      - The 'LiteLLM' logger is set to WARNING level and does not propagate to the root logger.

    Usage:
        from logging_config import setup_logging
        setup_logging()
    """
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
    lite_logger = logging.getLogger("LiteLLM")
    lite_logger.propagate = False  # 🚫 Prevent bubbling to root
    lite_logger.setLevel(logging.WARNING)  # 🔕 Suppress INFO logs
