"""Region of Interest (ROI) data model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ROI:
    """Represents the automatically detected rectangular area containing game content.
    
    Attributes:
        x: Top-left X coordinate
        y: Top-left Y coordinate
        width: Width of the region
        height: Height of the region
        detection_confidence: Confidence score from template matching (0.0-1.0)
        last_updated: Unix timestamp in milliseconds when ROI was last detected
    """
    x: int
    y: int
    width: int
    height: int
    detection_confidence: float = 0.0
    last_updated: Optional[int] = None  # Unix timestamp in milliseconds
    
    def to_dict(self) -> dict:
        """Convert ROI to dictionary for JSON serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "detection_confidence": self.detection_confidence,
            "last_updated": self.last_updated,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ROI":
        """Create ROI from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            detection_confidence=data.get("detection_confidence", 0.0),
            last_updated=data.get("last_updated"),
        )
    
    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """Return bounds as (x, y, x+width, y+height) tuple."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)
