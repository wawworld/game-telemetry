"""Session trigger monitoring service for automatic start/stop."""

import asyncio
from typing import List, Callable, Optional
from pynput import keyboard
from models.config import SessionTrigger
from utils.timestamps import unix_timestamp_ms
from utils.logging import get_logger

logger = get_logger(__name__)


class TriggerMonitor:
    """Monitors session triggers (keyboard, timeout, etc.) to automatically stop sessions."""
    
    def __init__(
        self,
        triggers: List[SessionTrigger],
        trigger_callback: Callable[[], None],
    ):
        """Initialize trigger monitor.
        
        Args:
            triggers: List of triggers to monitor (OR logic)
            trigger_callback: Function to call when any trigger is activated
        """
        self.triggers = triggers
        self.trigger_callback = trigger_callback
        self._running = False
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._timeout_task: Optional[asyncio.Task] = None
        self._start_time: Optional[int] = None
        
        # Parse triggers
        self._keyboard_triggers = []
        self._timeout_seconds: Optional[float] = None
        
        for trigger in triggers:
            if trigger.type == "keyboard":
                key = trigger.parameters.get("key")
                if key:
                    self._keyboard_triggers.append(key.lower())
            elif trigger.type == "timeout":
                duration = trigger.parameters.get("duration_seconds")
                if duration:
                    self._timeout_seconds = float(duration)
    
    async def start(self) -> None:
        """Start monitoring triggers."""
        if self._running:
            logger.warning("Trigger monitor already running")
            return
        
        self._running = True
        self._start_time = unix_timestamp_ms()
        
        # Start keyboard listener if needed
        if self._keyboard_triggers:
            self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self._keyboard_listener.start()
            logger.info(f"Keyboard trigger monitoring started: {self._keyboard_triggers}")
        
        # Start timeout monitor if needed
        if self._timeout_seconds:
            self._timeout_task = asyncio.create_task(self._timeout_monitor())
            logger.info(f"Timeout trigger monitoring started: {self._timeout_seconds}s")
        
        logger.info("Trigger monitor started")
    
    async def stop(self) -> None:
        """Stop monitoring triggers."""
        if not self._running:
            return
        
        self._running = False
        
        # Stop keyboard listener
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        
        # Cancel timeout task
        if self._timeout_task:
            self._timeout_task.cancel()
            try:
                await self._timeout_task
            except asyncio.CancelledError:
                pass
            self._timeout_task = None
        
        logger.info("Trigger monitor stopped")
    
    def _on_key_press(self, key) -> None:
        """Handle keyboard press events.
        
        Args:
            key: Key pressed
        """
        if not self._running:
            return
        
        try:
            # Get key name
            key_name = None
            if hasattr(key, 'char') and key.char:
                key_name = key.char.lower()
            elif hasattr(key, 'name'):
                key_name = key.name.lower()
            
            # Check if matches any trigger
            if key_name in self._keyboard_triggers:
                logger.info(f"Keyboard trigger activated: {key_name}")
                self._trigger_activated()
        
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    async def _timeout_monitor(self) -> None:
        """Monitor for timeout trigger."""
        try:
            await asyncio.sleep(self._timeout_seconds)
            
            if self._running:
                logger.info(f"Timeout trigger activated: {self._timeout_seconds}s elapsed")
                self._trigger_activated()
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in timeout monitor: {e}")
    
    def _trigger_activated(self) -> None:
        """Handle trigger activation."""
        if self._running and self.trigger_callback:
            # Call callback in a thread-safe way
            try:
                self.trigger_callback()
            except Exception as e:
                logger.error(f"Error calling trigger callback: {e}")
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since monitoring started.
        
        Returns:
            Elapsed seconds
        """
        if self._start_time:
            return (unix_timestamp_ms() - self._start_time) / 1000.0
        return 0.0
