"""Session manager for coordinating telemetry collection."""

import asyncio
from pathlib import Path
from typing import Optional
from models.session import Session
from models.config import GameConfig
from services.input_capture import InputCaptureService
from services.screen_capture import ScreenCaptureService
from services.event_buffer import EventBuffer
from services.writers.event_writer import EventWriter
from services.writers.metadata_writer import MetadataWriter
from services.writers.frame_writer import FrameWriter
from utils.timestamps import unix_timestamp_ms
from utils.logging import get_logger
import platform

logger = get_logger(__name__)


class SessionManager:
    """Manages telemetry collection sessions."""
    
    def __init__(self, config: GameConfig):
        """Initialize session manager.
        
        Args:
            config: Game configuration
        """
        self.config = config
        self.session: Optional[Session] = None
        
        # Services (initialized when session starts)
        self.input_capture: Optional[InputCaptureService] = None
        self.screen_capture: Optional[ScreenCaptureService] = None
        self.event_buffer: Optional[EventBuffer] = None
        
        # Writers
        self.event_writer: Optional[EventWriter] = None
        self.metadata_writer: Optional[MetadataWriter] = None
        self.frame_writer: Optional[FrameWriter] = None
        
        self._running = False
    
    async def start_session(self, participant_id: Optional[str] = None) -> Session:
        """Start a new telemetry collection session.
        
        Args:
            participant_id: Optional participant identifier
            
        Returns:
            Created session object
        """
        if self._running:
            raise RuntimeError("Session already running")
        
        # Create session
        self.session = Session(
            game_name=self.config.game_name,
            start_time=unix_timestamp_ms(),
            participant_id=participant_id,
            platform=platform.system(),
        )
        
        # Setup output directory
        output_dir = Path(self.config.output_directory) / self.session.session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting session {self.session.session_id}")
        logger.info(f"Output directory: {output_dir}")
        
        # Initialize writers
        self.event_writer = EventWriter(str(output_dir), self.session.session_id)
        self.metadata_writer = MetadataWriter(str(output_dir), self.session.session_id)
        self.frame_writer = FrameWriter(
            str(output_dir),
            self.session.session_id,
            self.config.capture_settings.image_format,
            self.config.capture_settings.image_quality,
        )
        
        # Write initial session metadata
        self.metadata_writer.write_sync(self.session)
        
        # Initialize event buffer
        self.event_buffer = EventBuffer(
            flush_callback=self.event_writer.write_batch,
            max_size=1000,
            flush_interval_seconds=1.0,
        )
        await self.event_buffer.start()
        
        # Initialize input capture
        self.input_capture = InputCaptureService(
            event_callback=self.event_buffer.add,
            enabled_event_types=self.config.capture_settings.enabled_event_types,
            game_id=self.config.game_name,
            session_id=self.session.session_id,
        )
        self.input_capture.start()
        
        # Initialize ROI detector if enabled (for initial detection only)
        self.roi_detector = None
        initial_roi = None
        
        if self.config.roi_detection.enabled:
            from services.roi_detector import ROIDetector
            
            # Create temporary detector for initial ROI
            roi_detector = ROIDetector(self.config.roi_detection, lambda roi: None)
            await roi_detector.start()
            
            # Wait briefly for initial detection
            await asyncio.sleep(0.5)
            initial_roi = roi_detector.get_roi_tuple()
            
            # Stop detector immediately after getting initial ROI
            await roi_detector.stop()
            logger.info(f"Initial ROI detected: {initial_roi}")
        
        # Initialize screen capture with fixed ROI
        self.screen_capture = ScreenCaptureService(
            frame_callback=self.frame_writer.write_sync,
            frame_rate=self.config.capture_settings.frame_rate,
            roi=initial_roi,
        )
        await self.screen_capture.start()
        
        self._running = True
        logger.info("Session started successfully")
        
        return self.session
    
    async def stop_session(self) -> None:
        """Stop the current telemetry collection session."""
        if not self._running:
            logger.warning("No session running")
            return
        
        logger.info(f"Stopping session {self.session.session_id}")
        
        # Stop capture services
        if self.input_capture:
            self.input_capture.stop()
        
        if self.screen_capture:
            await self.screen_capture.stop()
        
        # Stop and flush event buffer
        if self.event_buffer:
            await self.event_buffer.stop()
        
        # Update session end time
        if self.session:
            self.session.end_time = unix_timestamp_ms()
        
        # Close writers
        if self.event_writer:
            await self.event_writer.close()
        
        if self.frame_writer:
            await self.frame_writer.close()
        
        # Write final session metadata
        if self.metadata_writer and self.session:
            self.metadata_writer.write_sync(self.session)
            await self.metadata_writer.close()
        
        self._running = False
        logger.info("Session stopped successfully")
        
        # Log statistics
        if self.input_capture:
            logger.info(f"Input capture stats: {self.input_capture.get_stats()}")
        if self.screen_capture:
            logger.info(f"Screen capture stats: {self.screen_capture.get_stats()}")
        if self.event_buffer:
            logger.info(f"Event buffer stats: {self.event_buffer.get_stats()}")
    
    def is_running(self) -> bool:
        """Check if session is currently running."""
        return self._running
    
    def get_session(self) -> Optional[Session]:
        """Get current session object."""
        return self.session
