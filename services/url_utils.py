"""
URL Utilities
Copyright (c) 2025 Mac GunJon
Production-Grade URL Normalization
"""

from urllib.parse import urlparse

ALLOWED_SCHEMES = ("http", "https")


def normalize_url(url: str) -> str | None:
    """
    Normalize and validate a URL for monitoring.

    Returns:
        str: normalized URL
        None: if invalid
    """

    if not url or not isinstance(url, str):
        return None

    url = url.strip()

    # auto add scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    # scheme validation
    if parsed.scheme not in ALLOWED_SCHEMES:
        return None

    # must have domain
    if not parsed.netloc:
        return None

    # block obvious invalid domains
    if " " in parsed.netloc or "." not in parsed.netloc:
        return None

    # normalize (remove trailing slash)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path or ''}"
    normalized = normalized.rstrip("/")

    return normalized
