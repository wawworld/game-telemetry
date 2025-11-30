"""Main telemetry controller orchestrating the entire system."""

import asyncio
from typing import Optional
from pathlib import Path
from models.config import GameConfig
from services.config_loader import ConfigLoader
from services.session_manager import SessionManager
from services.game_detector import GameDetector
from services.trigger_monitor import TriggerMonitor
from utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


class TelemetryController:
    """Main orchestrator for the telemetry system."""
    
    def __init__(self):
        """Initialize telemetry controller."""
        self.config: Optional[GameConfig] = None
        self.session_manager: Optional[SessionManager] = None
        self.game_detector: Optional[GameDetector] = None
        self.trigger_monitor: Optional[TriggerMonitor] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
    
    def load_config(self, config_path: str) -> None:
        """Load game configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        logger.info(f"Loading configuration from {config_path}")
        self.config = ConfigLoader.load_config(config_path)
        
        # Initialize game detector
        self.game_detector = GameDetector(
            process_name=self.config.process_name,
            window_title=self.config.window_title,
            executable_path=self.config.executable_path,
        )
        
        # Initialize session manager
        self.session_manager = SessionManager(self.config)
        
        logger.info(f"Configuration loaded for game: {self.config.game_name}")
    
    async def start(self, participant_id: Optional[str] = None, wait_for_roi: bool = True) -> None:
        """Start telemetry collection.
        
        Args:
            participant_id: Optional participant identifier
            wait_for_roi: If True and ROI detection is enabled, wait for ROI detection before starting
        """
        if self._running:
            logger.warning("Telemetry already running")
            return
        
        if not self.config or not self.session_manager:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        
        logger.info("Starting telemetry collection")
        
        # Wait for ROI detection if enabled
        if wait_for_roi and self.config.roi_detection.enabled:
            logger.info("⏳ ROI 감지 대기 중... (최대 30초)")
            print("⏳ 게임 화면을 띄우고 기다리세요...")
            
            # Start ROI detector temporarily
            from services.roi_detector import ROIDetector
            
            roi_detected = False
            detected_roi = None
            
            def on_temp_roi(roi):
                nonlocal roi_detected, detected_roi
                if roi.detection_confidence > 0:
                    roi_detected = True
                    detected_roi = roi
            
            temp_detector = ROIDetector(self.config.roi_detection, on_temp_roi)
            await temp_detector.start()
            
            # Wait up to 30 seconds for detection
            for i in range(30):
                if roi_detected:
                    logger.info(f"✅ ROI 감지 완료! ({detected_roi.width}x{detected_roi.height}, 신뢰도: {detected_roi.detection_confidence:.1%})")
                    print(f"✅ 게임 영역 감지 완료! 녹화를 시작합니다...")
                    break
                await asyncio.sleep(1)
                if (i + 1) % 5 == 0:
                    logger.info(f"ROI 감지 대기 중... ({i + 1}/30초)")
            else:
                logger.warning("⚠️  ROI 자동 감지 실패. Fallback 영역 사용")
                print("⚠️  게임 영역을 찾지 못했습니다. 기본 영역으로 녹화합니다...")
            
            await temp_detector.stop()
            print()
        
        # Check if game is running
        if self.game_detector and not self.game_detector.is_game_running():
            logger.warning(f"Game '{self.config.game_name}' is not currently running")
            logger.info("Starting telemetry anyway - data will be collected regardless of game state")
        
        # Start session
        await self.session_manager.start_session(participant_id)
        
        # Start trigger monitor for session end triggers
        if self.config.session_end_triggers:
            self.trigger_monitor = TriggerMonitor(
                triggers=self.config.session_end_triggers,
                trigger_callback=self._on_end_trigger,
            )
            await self.trigger_monitor.start()
            
            # Log active triggers
            trigger_info = []
            for trigger in self.config.session_end_triggers:
                if trigger.type == "keyboard":
                    key = trigger.parameters.get("key", "?")
                    trigger_info.append(f"키보드({key})")
                elif trigger.type == "timeout":
                    duration = trigger.parameters.get("duration_seconds", 0)
                    trigger_info.append(f"타임아웃({duration}초)")
            
            logger.info(f"세션 종료 트리거 활성화: {', '.join(trigger_info)}")
        
        self._running = True
        logger.info("Telemetry collection started")
    
    async def stop(self) -> None:
        """Stop telemetry collection."""
        if not self._running:
            logger.warning("Telemetry not running")
            return
        
        logger.info("Stopping telemetry collection")
        
        # Stop trigger monitor
        if self.trigger_monitor:
            await self.trigger_monitor.stop()
            self.trigger_monitor = None
        
        # Stop session
        if self.session_manager:
            await self.session_manager.stop_session()
        
        self._running = False
        self._shutdown_event.set()
        logger.info("Telemetry collection stopped")
    
    def _on_end_trigger(self) -> None:
        """Callback for session end trigger activation."""
        logger.info("세션 종료 트리거 활성화됨")
        
        # Set shutdown event to trigger stop
        if self._running:
            self._shutdown_event.set()
    
    async def run_until_stopped(self) -> None:
        """Run telemetry collection until manually stopped."""
        if not self._running:
            raise RuntimeError("Telemetry not started. Call start() first.")
        
        logger.info("Running telemetry collection (press Ctrl+C to stop)")
        
        try:
            await self._shutdown_event.wait()
            # Stop was triggered
            await self.stop()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            await self.stop()
    
    def is_running(self) -> bool:
        """Check if telemetry is currently running."""
        return self._running
    
    def get_status(self) -> dict:
        """Get current status information.
        
        Returns:
            Status dictionary with current state
        """
        status = {
            "running": self._running,
            "config_loaded": self.config is not None,
            "game_name": self.config.game_name if self.config else None,
        }
        
        if self.session_manager and self.session_manager.is_running():
            session = self.session_manager.get_session()
            if session:
                status["session_id"] = session.session_id
                status["session_start_time"] = session.start_time
        
        return status


async def main():
    """Main entry point for running telemetry controller directly."""
    import sys
    
    # Setup logging
    setup_logging(log_level="INFO", log_to_console=True)
    
    if len(sys.argv) < 2:
        print("Usage: python -m telemetry_controller <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Create and run controller
    controller = TelemetryController()
    controller.load_config(config_file)
    
    await controller.start()
    await controller.run_until_stopped()


if __name__ == "__main__":
    asyncio.run(main())
