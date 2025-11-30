"""Telemetry event data model."""

from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime


@dataclass
class TelemetryEvent:
    """Represents a single recorded player action.
    
    Attributes:
        timestamp: Unix timestamp in milliseconds
        event_type: Type of event (keyboard_press, keyboard_release, mouse_click, mouse_move, mouse_scroll)
        parameters: Event-specific parameters (key code, mouse position, button ID, etc.)
        game_id: Identifier of the game being played
        session_id: Unique session identifier (UUID)
    """
    timestamp: int  # Unix timestamp in milliseconds
    event_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    game_id: str = ""
    session_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "parameters": self.parameters,
            "game_id": self.game_id,
            "session_id": self.session_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryEvent":
        """Create event from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            event_type=data["event_type"],
            parameters=data.get("parameters", {}),
            game_id=data.get("game_id", ""),
            session_id=data.get("session_id", ""),
        )
