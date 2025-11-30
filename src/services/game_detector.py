"""Game process detection service."""

import psutil
from typing import Optional
from utils.logging import get_logger

logger = get_logger(__name__)


class GameDetector:
    """Detects running game processes by name, window title, or executable path."""
    
    def __init__(
        self,
        process_name: Optional[str] = None,
        window_title: Optional[str] = None,
        executable_path: Optional[str] = None,
    ):
        """Initialize game detector.
        
        Args:
            process_name: Process name to match (e.g., "game.exe")
            window_title: Window title pattern to match
            executable_path: Full path to game executable
        """
        self.process_name = process_name
        self.window_title = window_title
        self.executable_path = executable_path
        
        if not any([process_name, window_title, executable_path]):
            raise ValueError("At least one detection method must be provided")
    
    def is_game_running(self) -> bool:
        """Check if the configured game is currently running.
        
        Returns:
            True if game is detected, False otherwise
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    # Check process name
                    if self.process_name and proc.info['name'] == self.process_name:
                        logger.debug(f"Game detected by process name: {self.process_name}")
                        return True
                    
                    # Check executable path
                    if self.executable_path and proc.info['exe'] == self.executable_path:
                        logger.debug(f"Game detected by exe path: {self.executable_path}")
                        return True
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # TODO: Window title matching requires platform-specific implementation
            # For now, only process name and executable path are supported
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting game: {e}")
            return False
    
    def get_game_process(self) -> Optional[psutil.Process]:
        """Get the game process object if running.
        
        Returns:
            Process object if found, None otherwise
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if self.process_name and proc.info['name'] == self.process_name:
                        return proc
                    
                    if self.executable_path and proc.info['exe'] == self.executable_path:
                        return proc
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting game process: {e}")
            return None
