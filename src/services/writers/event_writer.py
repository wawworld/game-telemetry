"""JSON Lines event writer for incremental event storage."""

import json
from pathlib import Path
from typing import List
from services.data_writer import DataWriter
from models.event import TelemetryEvent
from utils.logging import get_logger

logger = get_logger(__name__)


class EventWriter(DataWriter):
    """Writes telemetry events to JSON Lines format (one event per line)."""
    
    def __init__(self, output_directory: str, session_id: str):
        """Initialize event writer.
        
        Args:
            output_directory: Directory for output files
            session_id: Session identifier for filename
        """
        super().__init__(output_directory)
        self.session_id = session_id
        self.events_file = self.output_directory / "events.jsonl"
        self._file_handle = None
        self._events_written = 0
    
    async def write(self, event: TelemetryEvent) -> None:
        """Write a single event to file.
        
        Args:
            event: TelemetryEvent to write
        """
        if self._file_handle is None:
            self._file_handle = open(self.events_file, 'a', encoding='utf-8')
        
        try:
            json_line = json.dumps(event.to_dict())
            self._file_handle.write(json_line + '\n')
            self._events_written += 1
        except Exception as e:
            logger.error(f"Error writing event: {e}")
            raise
    
    def write_batch(self, events: List[TelemetryEvent]) -> None:
        """Write multiple events at once (synchronous for buffer callback).
        
        Args:
            events: List of TelemetryEvent objects
        """
        if self._file_handle is None:
            self._file_handle = open(self.events_file, 'a', encoding='utf-8')
        
        try:
            for event in events:
                json_line = json.dumps(event.to_dict())
                self._file_handle.write(json_line + '\n')
            self._file_handle.flush()
            self._events_written += len(events)
            logger.debug(f"Wrote {len(events)} events to {self.events_file}")
        except Exception as e:
            logger.error(f"Error writing event batch: {e}")
            raise
    
    async def flush(self) -> None:
        """Flush buffered data to disk."""
        if self._file_handle:
            self._file_handle.flush()
    
    async def close(self) -> None:
        """Close the file handle."""
        if self._file_handle:
            self._file_handle.flush()
            self._file_handle.close()
            self._file_handle = None
            logger.info(f"Closed event writer. Total events written: {self._events_written}")
    
    def get_events_count(self) -> int:
        """Get total number of events written."""
        return self._events_written
