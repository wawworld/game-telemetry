"""Input capture service using pynput for keyboard and mouse events."""

from typing import Callable, Optional, List
from pynput import keyboard, mouse
from models.event import TelemetryEvent
from utils.timestamps import unix_timestamp_ms
from utils.logging import get_logger

logger = get_logger(__name__)


class InputCaptureService:
    """Captures keyboard and mouse input events using pynput."""
    
    def __init__(
        self,
        event_callback: Callable[[TelemetryEvent], None],
        enabled_event_types: Optional[List[str]] = None,
        game_id: str = "",
        session_id: str = "",
    ):
        """Initialize input capture service.
        
        Args:
            event_callback: Function to call when event is captured
            enabled_event_types: List of event types to capture (None = all)
            game_id: Game identifier
            session_id: Session identifier
        """
        self.event_callback = event_callback
        self.enabled_event_types = enabled_event_types or [
            "keyboard_press", "keyboard_release",
            "mouse_click", "mouse_move", "mouse_scroll"
        ]
        self.game_id = game_id
        self.session_id = session_id
        
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._running = False
        self._pressed_keys = set()  # Track currently pressed keys
        self._stats = {
            "keyboard_events": 0,
            "mouse_events": 0,
            "total_events": 0,
        }
    
    def start(self) -> None:
        """Start capturing input events."""
        if self._running:
            logger.warning("Input capture already running")
            return
        
        # Start keyboard listener
        if any(et.startswith("keyboard") for et in self.enabled_event_types):
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
            )
            self._keyboard_listener.start()
        
        # Start mouse listener
        if any(et.startswith("mouse") for et in self.enabled_event_types):
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
                on_move=self._on_mouse_move,
                on_scroll=self._on_mouse_scroll,
            )
            self._mouse_listener.start()
        
        self._running = True
        logger.info(f"Input capture started (enabled types: {self.enabled_event_types})")
    
    def stop(self) -> None:
        """Stop capturing input events."""
        if not self._running:
            return
        
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        
        self._running = False
        logger.info(f"Input capture stopped. Stats: {self._stats}")
    
    def _create_event(self, event_type: str, parameters: dict) -> TelemetryEvent:
        """Create a telemetry event with current timestamp."""
        return TelemetryEvent(
            timestamp=unix_timestamp_ms(),
            event_type=event_type,
            parameters=parameters,
            game_id=self.game_id,
            session_id=self.session_id,
        )
    
    def _on_key_press(self, key) -> None:
        """Handle keyboard key press event."""
        if "keyboard_press" not in self.enabled_event_types:
            return
        
        try:
            # Get key representation
            key_str = str(key)
            
            # Skip unknown keys (e.g., <63> on macOS)
            if key_str.startswith('<') and key_str.endswith('>') and key_str[1:-1].isdigit():
                return
            
            # Skip if key is already pressed (OS key repeat)
            if key_str in self._pressed_keys:
                return
            
            # Mark key as pressed
            self._pressed_keys.add(key_str)
            
            if hasattr(key, 'char') and key.char is not None:
                key_value = key.char
            else:
                key_value = key_str
            
            event = self._create_event("keyboard_press", {
                "key": key_value,
                "key_code": key_str,
            })
            
            self.event_callback(event)
            self._stats["keyboard_events"] += 1
            self._stats["total_events"] += 1
            
        except Exception as e:
            logger.error(f"Error processing key press: {e}")
    
    def _on_key_release(self, key) -> None:
        """Handle keyboard key release event."""
        if "keyboard_release" not in self.enabled_event_types:
            return
        
        try:
            key_str = str(key)
            
            # Skip unknown keys (e.g., <63> on macOS)
            if key_str.startswith('<') and key_str.endswith('>') and key_str[1:-1].isdigit():
                return
            
            # Remove from pressed keys set
            self._pressed_keys.discard(key_str)
            
            if hasattr(key, 'char') and key.char is not None:
                key_value = key.char
            else:
                key_value = key_str
            
            event = self._create_event("keyboard_release", {
                "key": key_value,
                "key_code": key_str,
            })
            
            self.event_callback(event)
            self._stats["keyboard_events"] += 1
            self._stats["total_events"] += 1
            
        except Exception as e:
            logger.error(f"Error processing key release: {e}")
    
    def _on_mouse_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Handle mouse click event."""
        if "mouse_click" not in self.enabled_event_types:
            return
        
        try:
            event = self._create_event("mouse_click", {
                "x": x,
                "y": y,
                "button": str(button),
                "pressed": pressed,
            })
            
            self.event_callback(event)
            self._stats["mouse_events"] += 1
            self._stats["total_events"] += 1
            
        except Exception as e:
            logger.error(f"Error processing mouse click: {e}")
    
    def _on_mouse_move(self, x: int, y: int) -> None:
        """Handle mouse move event."""
        if "mouse_move" not in self.enabled_event_types:
            return
        
        try:
            event = self._create_event("mouse_move", {
                "x": x,
                "y": y,
            })
            
            self.event_callback(event)
            self._stats["mouse_events"] += 1
            self._stats["total_events"] += 1
            
        except Exception as e:
            logger.error(f"Error processing mouse move: {e}")
    
    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Handle mouse scroll event."""
        if "mouse_scroll" not in self.enabled_event_types:
            return
        
        try:
            event = self._create_event("mouse_scroll", {
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
            })
            
            self.event_callback(event)
            self._stats["mouse_events"] += 1
            self._stats["total_events"] += 1
            
        except Exception as e:
            logger.error(f"Error processing mouse scroll: {e}")
    
    def get_stats(self) -> dict:
        """Get capture statistics."""
        return self._stats.copy()
