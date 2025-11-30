"""Configuration loader service for game profiles."""

import yaml
import json
from pathlib import Path
from typing import Union, List
from models.config import GameConfig, ROIDetectionConfig, SessionTrigger, CaptureSettings
from utils.logging import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """Loads and validates game configuration files (YAML/JSON)."""
    
    @staticmethod
    def load_config(config_path: Union[str, Path]) -> GameConfig:
        """Load a single game configuration file.
        
        Args:
            config_path: Path to YAML or JSON configuration file
            
        Returns:
            GameConfig object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid or missing required fields
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Load file based on extension
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}. Use .yaml, .yml, or .json")
        
        if not data:
            raise ValueError(f"Empty configuration file: {config_path}")
        
        logger.info(f"Loaded configuration from {config_path}")
        return ConfigLoader._parse_config(data)
    
    @staticmethod
    def load_multiple_configs(config_paths: List[Union[str, Path]]) -> List[GameConfig]:
        """Load multiple game configuration files.
        
        Args:
            config_paths: List of paths to configuration files
            
        Returns:
            List of GameConfig objects
        """
        configs = []
        for path in config_paths:
            try:
                config = ConfigLoader.load_config(path)
                configs.append(config)
            except Exception as e:
                logger.error(f"Failed to load config {path}: {e}")
        
        logger.info(f"Loaded {len(configs)} game configurations")
        return configs
    
    @staticmethod
    def load_config_directory(directory: Union[str, Path]) -> List[GameConfig]:
        """Load all configuration files from a directory.
        
        Args:
            directory: Path to directory containing config files
            
        Returns:
            List of GameConfig objects
        """
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid configuration directory: {directory}")
        
        # Find all YAML and JSON files
        config_files = list(dir_path.glob("*.yaml")) + \
                      list(dir_path.glob("*.yml")) + \
                      list(dir_path.glob("*.json"))
        
        return ConfigLoader.load_multiple_configs(config_files)
    
    @staticmethod
    def _parse_config(data: dict) -> GameConfig:
        """Parse configuration dictionary into GameConfig object.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            GameConfig object
            
        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if "game_name" not in data:
            raise ValueError("Configuration must include 'game_name' field")
        
        # Parse ROI detection config
        roi_config = ROIDetectionConfig()
        if "roi_detection" in data:
            roi_data = data["roi_detection"]
            roi_config = ROIDetectionConfig(
                enabled=roi_data.get("enabled", False),
                reference_images=roi_data.get("reference_images", []),
                match_threshold=roi_data.get("match_threshold", 0.875),
                padding=roi_data.get("padding", 0),
                update_interval_seconds=roi_data.get("update_interval_seconds", 5.0),
                retry_interval_seconds=roi_data.get("retry_interval_seconds", 5.0),
                manual_fallback_coords=roi_data.get("manual_fallback_coords"),
            )
        
        # Parse session triggers
        start_triggers = []
        if "session_start_triggers" in data:
            for trigger_data in data["session_start_triggers"]:
                start_triggers.append(SessionTrigger(
                    type=trigger_data["type"],
                    parameters=trigger_data.get("parameters", {})
                ))
        
        end_triggers = []
        if "session_end_triggers" in data:
            for trigger_data in data["session_end_triggers"]:
                end_triggers.append(SessionTrigger(
                    type=trigger_data["type"],
                    parameters=trigger_data.get("parameters", {})
                ))
        
        # Parse capture settings
        capture_settings = CaptureSettings()
        if "capture_settings" in data:
            cs_data = data["capture_settings"]
            capture_settings = CaptureSettings(
                frame_rate=cs_data.get("frame_rate", 15),
                image_format=cs_data.get("image_format", "jpeg"),
                image_quality=cs_data.get("image_quality", 85),
                enabled_event_types=cs_data.get("enabled_event_types", capture_settings.enabled_event_types),
            )
        
        return GameConfig(
            game_name=data["game_name"],
            process_name=data.get("process_name"),
            window_title=data.get("window_title"),
            executable_path=data.get("executable_path"),
            roi_detection=roi_config,
            session_start_triggers=start_triggers,
            session_end_triggers=end_triggers,
            capture_settings=capture_settings,
            output_directory=data.get("output_directory", "data"),
        )
