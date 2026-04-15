# fog_node/utils/logger.py

import logging

from utils.timezone import now_ist_iso

# =========================
# Logger Configuration
# =========================

LOGGER_NAME = "fog_node_logger"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# Prevent duplicate handlers
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


# =========================
# Helper Logging Functions
# =========================

def log_info(message: str):
    logger.info(message)


def log_warning(message: str):
    logger.warning(message)


def log_error(message: str):
    logger.error(message)


def log_event(event: str, details: dict = None):
    """
    Structured event logging (recommended for security systems)
    """
    payload = {
        "event": event,
        "timestamp": now_ist_iso(),
        "details": details or {}
    }
    logger.info(payload)