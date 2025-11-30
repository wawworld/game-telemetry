"""ROI (Region of Interest) detection service using template matching."""

import asyncio
from pathlib import Path
from typing import Optional, List, Callable
import cv2
import numpy as np
from PIL import ImageGrab, Image
from models.roi import ROI
from models.config import ROIDetectionConfig
from utils.timestamps import unix_timestamp_ms
from utils.logging import get_logger

logger = get_logger(__name__)


class ROIDetector:
    """Detects game region on screen using template matching with reference images."""
    
    def __init__(
        self,
        config: ROIDetectionConfig,
        roi_update_callback: Optional[Callable[[Optional[ROI]], None]] = None,
    ):
        """Initialize ROI detector.
        
        Args:
            config: ROI detection configuration
            roi_update_callback: Function to call when ROI is detected/updated
        """
        self.config = config
        self.roi_update_callback = roi_update_callback
        self.current_roi: Optional[ROI] = None
        self._running = False
        self._detection_task: Optional[asyncio.Task] = None
        self._reference_templates: List[np.ndarray] = []
        
        # Load reference images
        if config.enabled:
            self._load_reference_images()
    
    def _load_reference_images(self) -> None:
        """Load and preprocess reference images for template matching."""
        for img_path in self.config.reference_images:
            path = Path(img_path)
            if not path.exists():
                logger.warning(f"Reference image not found: {img_path}")
                continue
            
            try:
                # Load image with OpenCV
                template = cv2.imread(str(path))
                if template is not None:
                    # Convert to grayscale for template matching
                    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                    self._reference_templates.append(template_gray)
                    logger.info(f"Loaded reference image: {img_path} (shape: {template_gray.shape})")
                else:
                    logger.error(f"Failed to load reference image: {img_path}")
            except Exception as e:
                logger.error(f"Error loading reference image {img_path}: {e}")
        
        if not self._reference_templates:
            logger.warning("No reference images loaded for ROI detection")
    
    async def start(self) -> None:
        """Start ROI detection loop."""
        if not self.config.enabled:
            logger.info("ROI detection is disabled")
            return
        
        if self._running:
            logger.warning("ROI detector already running")
            return
        
        self._running = True
        self._detection_task = asyncio.create_task(self._detection_loop())
        logger.info("ROI detector started")
    
    async def stop(self) -> None:
        """Stop ROI detection."""
        if not self._running:
            return
        
        self._running = False
        
        if self._detection_task:
            self._detection_task.cancel()
            try:
                await self._detection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("ROI detector stopped")
    
    async def _detection_loop(self) -> None:
        """Main detection loop with periodic updates."""
        while self._running:
            try:
                # Attempt to detect ROI
                detected_roi = await self._detect_roi()
                
                if detected_roi:
                    # Update current ROI
                    self.current_roi = detected_roi
                    logger.info(f"ROI detected: {detected_roi.to_dict()}")
                    
                    # Notify callback
                    if self.roi_update_callback:
                        self.roi_update_callback(detected_roi)
                    
                    # Wait for update interval
                    await asyncio.sleep(self.config.update_interval_seconds)
                else:
                    # Detection failed, use fallback or retry
                    logger.warning("ROI detection failed")
                    
                    if self.current_roi is None and self.config.manual_fallback_coords:
                        # Use manual fallback on first failure
                        fallback = ROI(
                            x=self.config.manual_fallback_coords.get("x", 0),
                            y=self.config.manual_fallback_coords.get("y", 0),
                            width=self.config.manual_fallback_coords.get("width", 1920),
                            height=self.config.manual_fallback_coords.get("height", 1080),
                            detection_confidence=0.0,
                            last_updated=unix_timestamp_ms(),
                        )
                        self.current_roi = fallback
                        logger.info(f"Using manual fallback ROI: {fallback.to_dict()}")
                        
                        if self.roi_update_callback:
                            self.roi_update_callback(fallback)
                    
                    # Wait for retry interval
                    await asyncio.sleep(self.config.retry_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ROI detection loop: {e}")
                await asyncio.sleep(self.config.retry_interval_seconds)
    
    async def _detect_roi(self) -> Optional[ROI]:
        """Detect ROI using template matching.
        
        Returns:
            Detected ROI or None if detection failed
        """
        if not self._reference_templates:
            return None
        
        try:
            # Capture full screen
            screenshot = await asyncio.get_event_loop().run_in_executor(
                None, ImageGrab.grab
            )
            
            # Convert PIL Image to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            
            best_match = None
            best_confidence = 0.0
            
            # Try each reference template
            for template in self._reference_templates:
                # Perform template matching
                result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Check if match exceeds threshold
                if max_val > self.config.match_threshold and max_val > best_confidence:
                    best_confidence = max_val
                    template_h, template_w = template.shape
                    
                    # Calculate ROI with padding
                    x = max(0, max_loc[0] - self.config.padding)
                    y = max(0, max_loc[1] - self.config.padding)
                    width = template_w + (2 * self.config.padding)
                    height = template_h + (2 * self.config.padding)
                    
                    # Clamp to screen bounds
                    screen_w, screen_h = screenshot.size
                    if x + width > screen_w:
                        width = screen_w - x
                    if y + height > screen_h:
                        height = screen_h - y
                    
                    best_match = ROI(
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        detection_confidence=float(best_confidence),
                        last_updated=unix_timestamp_ms(),
                    )
                    
                    logger.debug(f"Template match: confidence={max_val:.3f}, location={max_loc}")
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error detecting ROI: {e}")
            return None
    
    def get_current_roi(self) -> Optional[ROI]:
        """Get the currently detected ROI.
        
        Returns:
            Current ROI or None if not detected
        """
        return self.current_roi
    
    def get_roi_tuple(self) -> Optional[tuple]:
        """Get current ROI as (x, y, width, height) tuple for screen capture.
        
        Returns:
            ROI tuple or None for full screen
        """
        if self.current_roi:
            return (
                self.current_roi.x,
                self.current_roi.y,
                self.current_roi.width,
                self.current_roi.height,
            )
        return None
