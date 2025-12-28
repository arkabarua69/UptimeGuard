"""
Configuration Loader
Copyright (c) 2025 Mac GunJon
Production-Grade Environment Configuration
"""

import os
import sys
from dotenv import load_dotenv
from core.logger import setup_logger

# --------------------------------------------------
# LOAD ENV
# --------------------------------------------------
load_dotenv()
logger = setup_logger()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def get_env_str(key: str, required: bool=False, default: str | None=None):
    value = os.getenv(key, default)
    if required and not value:
        logger.critical(f"Missing required environment variable: {key}")
        sys.exit(1)
    return value


def get_env_int(key: str, default: int, min_value: int | None=None):
    raw = os.getenv(key, str(default))
    try:
        value = int(raw)
    except ValueError:
        logger.warning(
            f"Invalid integer for {key}='{raw}', falling back to {default}"
        )
        value = default

    if min_value is not None and value < min_value:
        logger.warning(
            f"{key}={value} is below minimum {min_value}, using {min_value}"
        )
        value = min_value

    return value


# --------------------------------------------------
# CORE BOT CONFIG
# --------------------------------------------------
BOT_TOKEN = get_env_str("DISCORD_TOKEN", required=True)

# --------------------------------------------------
# MONITORING CONFIG
# --------------------------------------------------
CHECK_INTERVAL = get_env_int(
    key="CHECK_INTERVAL",
    default=60,
    min_value=10,  # prevent abuse / rate limits
)

REQUEST_TIMEOUT = get_env_int(
    key="REQUEST_TIMEOUT",
    default=10,
    min_value=5,
)

# --------------------------------------------------
# ENV INFO (LOG ONLY)
# --------------------------------------------------
ENVIRONMENT = get_env_str("ENVIRONMENT", default="production")

logger.info(
    f"Config loaded | ENV={ENVIRONMENT} | "
    f"CHECK_INTERVAL={CHECK_INTERVAL}s | TIMEOUT={REQUEST_TIMEOUT}s"
)

ALERT_FAILURE_THRESHOLD = get_env_int(
    key="ALERT_FAILURE_THRESHOLD",
    default=3,
    min_value=1,
)

ALERT_CHANNEL_ID = int(
    get_env_str("ALERT_CHANNEL_ID", default="0")
)
