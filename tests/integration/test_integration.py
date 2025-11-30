"""Integration tests for the telemetry system."""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from telemetry_controller import TelemetryController
from services.session_manager import SessionManager
from models.config import GameConfig, CaptureSettings


class TestTelemetryController:
    """Integration tests for TelemetryController."""
    
    def test_controller_initialization(self):
        """Test that controller initializes correctly."""
        controller = TelemetryController()
        
        assert controller.config is None
        assert controller.session_manager is None
        assert controller.game_detector is None
        assert controller._running is False
    
    def test_load_config(self):
        """Test loading configuration."""
        controller = TelemetryController()
        controller.load_config("configs/sample_game.yaml")
        
        assert controller.config is not None
        assert controller.config.game_name == "Sample Game"
        assert controller.game_detector is not None
        assert controller.session_manager is not None
    
    @pytest.mark.asyncio
    async def test_start_and_stop_session(self):
        """Test starting and stopping a session."""
        controller = TelemetryController()
        controller.load_config("configs/sample_game.yaml")
        
        # Start session
        await controller.start(participant_id="test_integration")
        
        assert controller._running is True
        assert controller.session_manager.session is not None
        
        # Wait briefly
        await asyncio.sleep(1)
        
        # Stop session
        await controller.stop()
        
        assert controller._running is False


class TestSessionManager:
    """Integration tests for SessionManager."""
    
    @pytest.mark.asyncio
    async def test_full_session_lifecycle(self):
        """Test complete session lifecycle."""
        # Create temporary config
        with tempfile.TemporaryDirectory() as tmpdir:
            config = GameConfig(
                game_name="Test Game",
                process_name="test.exe",
                capture_settings=CaptureSettings(
                    frame_rate=10,
                    image_format="jpeg",
                    image_quality=85,
                    enabled_event_types=["keyboard_press"]
                ),
                output_directory=tmpdir
            )
            
            manager = SessionManager(config)
            
            # Start session
            session = await manager.start_session(participant_id="test_user")
            
            assert session is not None
            assert session.game_name == "Test Game"
            assert session.participant_id == "test_user"
            assert session.start_time > 0
            
            # Check output directory created
            session_dir = Path(tmpdir) / session.session_id
            assert session_dir.exists()
            
            # Check session.json created
            session_file = session_dir / "session.json"
            assert session_file.exists()
            
            # Wait briefly for some data collection
            await asyncio.sleep(0.5)
            
            # Stop session
            await manager.stop_session()
            
            # Verify end time was set
            with open(session_file) as f:
                data = json.load(f)
                assert data["end_time"] is not None
                assert data["end_time"] > data["start_time"]


class TestEndToEnd:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_complete_telemetry_collection_cycle(self):
        """Test a complete telemetry collection cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test config file
            test_config = {
                "game_name": "Integration Test Game",
                "process_name": "test_process.exe",
                "session_start_triggers": [{"type": "manual", "parameters": {}}],
                "session_end_triggers": [
                    {"type": "keyboard", "parameters": {"key": "F9"}}
                ],
                "capture_settings": {
                    "frame_rate": 5,
                    "image_format": "jpeg",
                    "image_quality": 75,
                    "enabled_event_types": ["keyboard_press", "mouse_click"]
                },
                "output_directory": tmpdir
            }
            
            config_path = Path(tmpdir) / "test_config.yaml"
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(test_config, f)
            
            # Run telemetry collection
            controller = TelemetryController()
            controller.load_config(str(config_path))
            
            await controller.start(participant_id="e2e_test")
            
            # Collect for 2 seconds
            await asyncio.sleep(2)
            
            await controller.stop()
            
            # Verify outputs - find session directories (UUID named)
            tmpdir_path = Path(tmpdir)
            all_items = list(tmpdir_path.iterdir())
            
            # Filter out the config file, find session UUID directories
            session_dirs = [d for d in all_items if d.is_dir()]
            assert len(session_dirs) > 0, f"No session directories found in {tmpdir}"
            
            session_dir = session_dirs[0]
            
            # Check session.json exists
            session_file = session_dir / "session.json"
            assert session_file.exists(), f"session.json not found in {session_dir}"
            
            with open(session_file) as f:
                session_data = json.load(f)
                assert session_data["game_name"] == "Integration Test Game"
                assert session_data["participant_id"] == "e2e_test"
                assert session_data["start_time"] > 0
                assert session_data["end_time"] > session_data["start_time"]
            
            # Check frames were captured (at 5 FPS for 2 seconds = ~10 frames)
            frames = list(session_dir.glob("frame_*.jpg"))
            assert len(frames) >= 5  # At least some frames captured
            
            # Verify frame filename format
            for frame in frames:
                name = frame.stem  # e.g., "frame_1234567890123"
                parts = name.split("_")
                assert len(parts) == 2
                assert parts[0] == "frame"
                assert parts[1].isdigit()
                assert len(parts[1]) == 13  # Unix ms timestamp


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_load_invalid_config_raises_error(self):
        """Test that loading invalid config raises appropriate error."""
        controller = TelemetryController()
        
        with pytest.raises(FileNotFoundError):
            controller.load_config("nonexistent_config.yaml")
    
    @pytest.mark.asyncio
    async def test_cannot_start_without_config(self):
        """Test that starting without config raises error."""
        controller = TelemetryController()
        
        with pytest.raises(Exception):
            await controller.start()
