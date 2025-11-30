"""Unit tests for utility functions."""

import pytest
from datetime import datetime, timezone
from utils.timestamps import (
    unix_timestamp_ms,
    iso8601_timestamp,
    unix_ms_to_iso8601,
    iso8601_to_unix_ms
)


class TestTimestamps:
    """Test timestamp utility functions."""
    
    def test_unix_timestamp_ms_format(self):
        """Test that unix_timestamp_ms returns milliseconds."""
        ts = unix_timestamp_ms()
        
        # Should be a 13-digit number (milliseconds since epoch)
        assert isinstance(ts, int)
        assert ts > 1_000_000_000_000  # After 2001
        assert ts < 2_000_000_000_000  # Before 2033
    
    def test_iso8601_timestamp_format(self):
        """Test that iso8601_timestamp returns valid ISO 8601 string."""
        ts = iso8601_timestamp()
        
        assert isinstance(ts, str)
        assert "T" in ts  # Date-time separator
        assert ":" in ts  # Time separator
        # Should be parseable back to datetime
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        assert isinstance(dt, datetime)
    
    def test_ms_to_iso8601_conversion(self):
        """Test converting milliseconds to ISO 8601."""
        # Known timestamp: 2025-01-01 00:00:00 UTC
        ms = 1735689600000
        iso = unix_ms_to_iso8601(ms)
        
        assert isinstance(iso, str)
        assert "2025" in iso
        assert "T" in iso
    
    def test_iso8601_to_ms_conversion(self):
        """Test converting ISO 8601 to milliseconds."""
        iso = "2025-01-01T00:00:00+00:00"
        ms = iso8601_to_unix_ms(iso)
        
        assert isinstance(ms, int)
        assert ms == 1735689600000
    
    def test_round_trip_conversion(self):
        """Test that conversion is reversible."""
        original_ms = 1735689600000
        
        # ms -> iso -> ms
        iso = unix_ms_to_iso8601(original_ms)
        result_ms = iso8601_to_unix_ms(iso)
        
        assert result_ms == original_ms
    
    def test_current_timestamp_reasonable(self):
        """Test that current timestamps are reasonable."""
        ms = unix_timestamp_ms()
        iso = iso8601_timestamp()
        
        # Convert ISO back to ms
        iso_ms = iso8601_to_unix_ms(iso)
        
        # Should be within 1 second of each other
        assert abs(ms - iso_ms) < 1000
