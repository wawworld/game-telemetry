"""JSON metadata writer for session metadata."""

import json
from pathlib import Path
from services.data_writer import DataWriter
from models.session import Session
from utils.logging import get_logger

logger = get_logger(__name__)


class MetadataWriter(DataWriter):
    """Writes session metadata to a single JSON file."""
    
    def __init__(self, output_directory: str, session_id: str):
        """Initialize metadata writer.
        
        Args:
            output_directory: Directory for output files
            session_id: Session identifier for filename
        """
        super().__init__(output_directory)
        self.session_id = session_id
        self.metadata_file = self.output_directory / "session.json"
        self._session_data = None
    
    async def write(self, session: Session) -> None:
        """Write session metadata to file.
        
        Args:
            session: Session object to write
        """
        self._session_data = session
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2)
            logger.debug(f"Wrote session metadata to {self.metadata_file}")
        except Exception as e:
            logger.error(f"Error writing session metadata: {e}")
            raise
    
    def write_sync(self, session: Session) -> None:
        """Synchronous write for non-async contexts.
        
        Args:
            session: Session object to write
        """
        self._session_data = session
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2)
            logger.debug(f"Wrote session metadata to {self.metadata_file}")
        except Exception as e:
            logger.error(f"Error writing session metadata: {e}")
            raise
    
    async def flush(self) -> None:
        """Flush is not needed for single-file writes."""
        pass
    
    async def close(self) -> None:
        """Close writer (final metadata write if needed)."""
        if self._session_data:
            await self.write(self._session_data)
            logger.info(f"Closed metadata writer for session {self.session_id}")
