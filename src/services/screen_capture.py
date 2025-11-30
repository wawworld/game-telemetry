"""Screen capture service for capturing game frames."""

import asyncio
from typing import Callable, Optional
from PIL import ImageGrab, Image
from utils.timestamps import unix_timestamp_ms
from utils.logging import get_logger

logger = get_logger(__name__)


class ScreenCaptureService:
    """Captures screen at configurable frame rate using Pillow."""
    
    def __init__(
        self,
        frame_callback: Callable[[Image.Image, int], None],
        frame_rate: int = 15,
        roi: Optional[tuple] = None,
    ):
        """Initialize screen capture service.
        
        Args:
            frame_callback: Function to call with captured frame and timestamp
            frame_rate: Frames per second to capture
            roi: Optional region of interest as (x, y, width, height) tuple
        """
        self.frame_callback = frame_callback
        self.frame_rate = frame_rate
        self.roi = roi
        self._running = False
        self._capture_task: Optional[asyncio.Task] = None
        self._stats = {
            "frames_captured": 0,
            "capture_errors": 0,
        }
    
    async def start(self) -> None:
        """Start capturing screen frames."""
        if self._running:
            logger.warning("Screen capture already running")
            return
        
        self._running = True
        self._capture_task = asyncio.create_task(self._capture_loop())
        logger.info(f"Screen capture started at {self.frame_rate} FPS")
    
    async def stop(self) -> None:
        """Stop capturing screen frames."""
        if not self._running:
            return
        
        self._running = False
        
        if self._capture_task:
            self._capture_task.cancel()
            try:
                await self._capture_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"Screen capture stopped. Stats: {self._stats}")
    
    async def _capture_loop(self) -> None:
        """Main capture loop."""
        interval = 1.0 / self.frame_rate  # seconds between captures
        
        while self._running:
            try:
                # Capture frame
                timestamp = unix_timestamp_ms()
                
                if self.roi:
                    # Capture specific region
                    x, y, width, height = self.roi
                    bbox = (x, y, x + width, y + height)
                    frame = ImageGrab.grab(bbox=bbox)
                else:
                    # Capture full screen
                    frame = ImageGrab.grab()
                
                # Call callback with frame and timestamp
                await asyncio.get_event_loop().run_in_executor(
                    None, self.frame_callback, frame, timestamp
                )
                
                self._stats["frames_captured"] += 1
                
                # Wait for next capture
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error capturing frame: {e}")
                self._stats["capture_errors"] += 1
                await asyncio.sleep(interval)
    
    def set_roi(self, roi: Optional[tuple]) -> None:
        """Update region of interest.
        
        Args:
            roi: Region as (x, y, width, height) tuple, or None for full screen
        """
        self.roi = roi
        if roi:
            logger.info(f"ROI updated to: {roi}")
        else:
            logger.info("ROI cleared, capturing full screen")
    
    def set_frame_rate(self, frame_rate: int) -> None:
        """Update frame rate.
        
        Args:
            frame_rate: New frames per second
        """
        self.frame_rate = frame_rate
        logger.info(f"Frame rate updated to {frame_rate} FPS")
    
    def get_stats(self) -> dict:
        """Get capture statistics."""
        return self._stats.copy()
