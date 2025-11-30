"""Collection session data model."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class Session:
    """Represents a continuous period of telemetry recording.
    
    Attributes:
        session_id: Unique identifier (UUID format)
        game_name: Name of the game being recorded
        start_time: Session start timestamp (ISO 8601 or Unix ms)
        end_time: Session end timestamp (ISO 8601 or Unix ms), None if active
        participant_id: Optional participant identifier (can be anonymized hash)
        game_version: Game version if detectable
        platform: Operating system (Windows/macOS/Linux)
        metadata: Additional session metadata
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    game_name: str = ""
    start_time: Optional[int] = None  # Unix timestamp in milliseconds
    end_time: Optional[int] = None  # Unix timestamp in milliseconds
    participant_id: Optional[str] = None
    game_version: Optional[str] = None
    platform: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "game_name": self.game_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "participant_id": self.participant_id,
            "game_version": self.game_version,
            "platform": self.platform,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary."""
        return cls(
            session_id=data.get("session_id", str(uuid.uuid4())),
            game_name=data.get("game_name", ""),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            participant_id=data.get("participant_id"),
            game_version=data.get("game_version"),
            platform=data.get("platform"),
            metadata=data.get("metadata", {}),
        )
