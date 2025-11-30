"""Abstract base class for data writers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DataWriter(ABC):
    """Abstract interface for writing telemetry data to storage.
    
    All concrete writer implementations (event, frame, metadata) must inherit
    from this base class and implement the write method.
    """
    
    def __init__(self, output_directory: str):
        """Initialize data writer.
        
        Args:
            output_directory: Base directory for output files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    async def write(self, data: Any) -> None:
        """Write data to storage.
        
        Args:
            data: Data to write (type depends on concrete implementation)
        """
        pass
    
    @abstractmethod
    async def flush(self) -> None:
        """Flush any buffered data to storage."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close writer and release resources."""
        pass
