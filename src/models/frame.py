"""Screen capture frame data model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Frame:
    """Represents a captured screen image at a specific timestamp.
    
    Attributes:
        timestamp: Unix timestamp in milliseconds when frame was captured
        image_path: Relative path to the saved image file (frame_<timestamp>.jpg)
        session_id: Unique session identifier (UUID)
    """
    timestamp: int  # Unix timestamp in milliseconds
    image_path: str
    session_id: str = ""
    
    def to_dict(self) -> dict:
        """Convert frame to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "image_path": self.image_path,
            "session_id": self.session_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Frame":
        """Create frame from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            image_path=data["image_path"],
            session_id=data.get("session_id", ""),
        )
