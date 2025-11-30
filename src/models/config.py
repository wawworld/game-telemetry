"""Game configuration data model."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ROIDetectionConfig:
    """Configuration for Region of Interest detection."""
    enabled: bool = False
    reference_images: List[str] = field(default_factory=list)
    match_threshold: float = 0.875  # Default: 87.5% (moderate matching)
    padding: int = 0
    update_interval_seconds: float = 5.0
    retry_interval_seconds: float = 5.0
    manual_fallback_coords: Optional[Dict[str, int]] = None  # {x, y, width, height}


@dataclass
class SessionTrigger:
    """Configuration for session start/end triggers."""
    type: str  # "manual", "keyboard", "timeout", "inactivity", "image"
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CaptureSettings:
    """Configuration for capture behavior."""
    frame_rate: int = 15  # FPS
    image_format: str = "jpeg"  # "jpeg" or "png"
    image_quality: int = 85  # For JPEG: 0-100
    enabled_event_types: List[str] = field(default_factory=lambda: [
        "keyboard_press", "keyboard_release",
        "mouse_click", "mouse_move", "mouse_scroll"
    ])


@dataclass
class GameConfig:
    """Complete game configuration including identification and observation settings.
    
    Attributes:
        game_name: Human-readable game name
        process_name: Process name for detection (optional)
        window_title: Window title pattern for detection (optional)
        executable_path: Full path to game executable (optional)
        roi_detection: ROI detection configuration
        session_start_triggers: List of triggers that start a session (OR logic)
        session_end_triggers: List of triggers that end a session (OR logic)
        capture_settings: Frame rate, image quality, event types
        output_directory: Where to store telemetry data
    """
    game_name: str
    process_name: Optional[str] = None
    window_title: Optional[str] = None
    executable_path: Optional[str] = None
    roi_detection: ROIDetectionConfig = field(default_factory=ROIDetectionConfig)
    session_start_triggers: List[SessionTrigger] = field(default_factory=list)
    session_end_triggers: List[SessionTrigger] = field(default_factory=list)
    capture_settings: CaptureSettings = field(default_factory=CaptureSettings)
    output_directory: str = "data"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization."""
        return {
            "game_name": self.game_name,
            "process_name": self.process_name,
            "window_title": self.window_title,
            "executable_path": self.executable_path,
            "roi_detection": {
                "enabled": self.roi_detection.enabled,
                "reference_images": self.roi_detection.reference_images,
                "match_threshold": self.roi_detection.match_threshold,
                "padding": self.roi_detection.padding,
                "update_interval_seconds": self.roi_detection.update_interval_seconds,
                "retry_interval_seconds": self.roi_detection.retry_interval_seconds,
                "manual_fallback_coords": self.roi_detection.manual_fallback_coords,
            },
            "session_start_triggers": [
                {"type": t.type, "parameters": t.parameters}
                for t in self.session_start_triggers
            ],
            "session_end_triggers": [
                {"type": t.type, "parameters": t.parameters}
                for t in self.session_end_triggers
            ],
            "capture_settings": {
                "frame_rate": self.capture_settings.frame_rate,
                "image_format": self.capture_settings.image_format,
                "image_quality": self.capture_settings.image_quality,
                "enabled_event_types": self.capture_settings.enabled_event_types,
            },
            "output_directory": self.output_directory,
        }
