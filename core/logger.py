"""
Logger Setup
Copyright (c) 2025 Mac GunJon
Production-Grade Logging System
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------
LOGGER_NAME = "UptimeGuard"
DEFAULT_LEVEL = "INFO"
LOG_FILE = os.getenv("LOG_FILE", "uptimeguard.log")
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


# --------------------------------------------------
# LOGGER FACTORY
# --------------------------------------------------
def setup_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    # Prevent duplicate handlers (CRITICAL for reloads)
    if logger.handlers:
        return logger

    # --------------------------------------------------
    # LOG LEVEL
    # --------------------------------------------------
    level_name = os.getenv("LOG_LEVEL", DEFAULT_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    # --------------------------------------------------
    # FORMATTERS
    # --------------------------------------------------
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --------------------------------------------------
    # CONSOLE HANDLER (RENDER SAFE)
    # --------------------------------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # --------------------------------------------------
    # FILE HANDLER (OPTIONAL, ROTATING)
    # --------------------------------------------------
    if os.getenv("ENABLE_FILE_LOGGING", "false").lower() == "true":
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    # --------------------------------------------------
    # SAFETY FLAGS
    # --------------------------------------------------
    logger.propagate = False

    logger.info(
        f"Logger initialized | Level={level_name} | FileLogging="
        f"{os.getenv('ENABLE_FILE_LOGGING', 'false')}"
    )

    return logger
