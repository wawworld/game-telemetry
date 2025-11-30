"""Timestamp utility functions."""

import time
from datetime import datetime, timezone


def unix_timestamp_ms() -> int:
    """Get current Unix timestamp in milliseconds.
    
    Returns:
        Current timestamp as integer milliseconds since epoch
    """
    return int(time.time() * 1000)


def iso8601_timestamp() -> str:
    """Get current timestamp in ISO 8601 format.
    
    Returns:
        Current timestamp as ISO 8601 string (UTC)
    """
    return datetime.now(timezone.utc).isoformat()


def unix_ms_to_iso8601(timestamp_ms: int) -> str:
    """Convert Unix milliseconds timestamp to ISO 8601 string.
    
    Args:
        timestamp_ms: Unix timestamp in milliseconds
        
    Returns:
        ISO 8601 formatted timestamp string
    """
    dt = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
    return dt.isoformat()


def iso8601_to_unix_ms(iso_string: str) -> int:
    """Convert ISO 8601 string to Unix milliseconds timestamp.
    
    Args:
        iso_string: ISO 8601 formatted timestamp string
        
    Returns:
        Unix timestamp in milliseconds
    """
    dt = datetime.fromisoformat(iso_string)
    return int(dt.timestamp() * 1000)
