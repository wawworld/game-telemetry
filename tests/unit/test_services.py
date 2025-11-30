"""Unit tests for service components."""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from services.config_loader import ConfigLoader
from services.event_buffer import EventBuffer
from models.event import TelemetryEvent
from models.config import GameConfig


class TestConfigLoader:
    """Test ConfigLoader service."""
    
    def test_load_valid_yaml_config(self):
        """Test loading valid YAML configuration."""
        config = ConfigLoader.load_config("configs/sample_game.yaml")
        
        assert isinstance(config, GameConfig)
        assert config.game_name == "Sample Game"
        assert config.process_name == "game.exe"
        assert config.capture_settings.frame_rate == 15
        assert config.output_directory == "data/sample_game"
    
    def test_config_has_required_fields(self):
        """Test that loaded config has all required fields."""
        config = ConfigLoader.load_config("configs/sample_game.yaml")
        
        # Required fields
        assert config.game_name is not None
        assert config.process_name is not None
        assert config.capture_settings is not None
        assert config.output_directory is not None
        
        # Capture settings
        assert config.capture_settings.frame_rate > 0
        assert config.capture_settings.image_format in ["jpeg", "png"]
        assert 0 <= config.capture_settings.image_quality <= 100
        assert len(config.capture_settings.enabled_event_types) > 0
    
    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_config("nonexistent.yaml")


class TestEventBuffer:
    """Test EventBuffer service."""
    
    @pytest.mark.asyncio
    async def test_add_event_to_buffer(self):
        """Test adding event to buffer."""
        flush_callback = Mock()
        buffer = EventBuffer(flush_callback=flush_callback, max_size=10)
        
        await buffer.start()
        
        event = TelemetryEvent(
            timestamp=1000,
            event_type="keyboard_press",
            game_id="game",
            session_id="session",
            parameters={"key": "a"}
        )
        
        buffer.add(event)
        
        await buffer.stop()
        
        # Should have called flush
        assert flush_callback.called
    
    @pytest.mark.asyncio
    async def test_buffer_flushes_when_full(self):
        """Test that buffer flushes when reaching max size."""
        flush_callback = Mock()
        buffer = EventBuffer(flush_callback=flush_callback, max_size=3)
        
        await buffer.start()
        
        # Add 3 events to trigger flush
        for i in range(3):
            event = TelemetryEvent(
                timestamp=i,
                event_type="keyboard_press",
                game_id="game",
                session_id="session",
                parameters={"key": str(i)}
            )
            buffer.add(event)
        
        # Give time for flush to occur
        await asyncio.sleep(0.1)
        
        await buffer.stop()
        
        # Should have flushed at least once
        assert flush_callback.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_buffer_periodic_flush(self):
        """Test that buffer flushes periodically."""
        flush_callback = Mock()
        buffer = EventBuffer(
            flush_callback=flush_callback,
            max_size=1000,
            flush_interval_seconds=0.5  # Short interval for testing
        )
        
        await buffer.start()
        
        # Add one event
        event = TelemetryEvent(
            timestamp=1000,
            event_type="mouse_click",
            game_id="game",
            session_id="session",
            parameters={"button": "left"}
        )
        buffer.add(event)
        
        # Wait for periodic flush
        await asyncio.sleep(0.6)
        
        await buffer.stop()
        
        # Should have flushed due to interval
        assert flush_callback.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_get_buffer_stats(self):
        """Test getting buffer statistics."""
        flush_callback = Mock()
        buffer = EventBuffer(flush_callback=flush_callback, max_size=10)
        
        await buffer.start()
        
        # Add events
        for i in range(5):
            event = TelemetryEvent(
                timestamp=i,
                event_type="keyboard_press",
                game_id="game",
                session_id="session",
                parameters={"key": str(i)}
            )
            buffer.add(event)
        
        stats = buffer.get_stats()
        
        await buffer.stop()
        
        assert "items_buffered" in stats
        assert "flush_count" in stats
        assert stats["items_buffered"] >= 5


class TestGameDetector:
    """Test GameDetector service."""
    
    def test_detector_initialization(self):
        """Test that GameDetector can be initialized."""
        from services.game_detector import GameDetector
        
        detector = GameDetector(
            process_name="test.exe",
            window_title="Test Window",
            executable_path="/usr/bin/test"
        )
        
        assert detector.process_name == "test.exe"
        assert detector.window_title == "Test Window"
        assert detector.executable_path == "/usr/bin/test"
    
    def test_is_running_returns_bool(self):
        """Test that is_game_running returns boolean."""
        from services.game_detector import GameDetector
        
        detector = GameDetector(process_name="nonexistent_process_12345.exe")
        result = detector.is_game_running()
        
        assert isinstance(result, bool)
        assert result is False  # Should not find this process


class TestDataWriters:
    """Test data writer services."""
    
    def test_event_writer_creates_file(self):
        """Test that EventWriter creates output file."""
        from services.writers.event_writer import EventWriter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = EventWriter(tmpdir, "test_session")
            
            event = TelemetryEvent(
                timestamp=1000,
                event_type="keyboard_press",
                game_id="game",
                session_id="session",
                parameters={"key": "a"}
            )
            
            writer.write_batch([event])
            
            # Check file exists
            events_file = Path(tmpdir) / "events.jsonl"
            assert events_file.exists()
            
            # Check content
            with open(events_file) as f:
                line = f.readline()
                data = json.loads(line)
                assert data["event_type"] == "keyboard_press"
                assert data["timestamp"] == 1000
    
    def test_metadata_writer_creates_file(self):
        """Test that MetadataWriter creates session.json."""
        from services.writers.metadata_writer import MetadataWriter
        from models.session import Session
        
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MetadataWriter(tmpdir, "test_session")
            
            session = Session(
                game_name="Test Game",
                start_time=1000,
                participant_id="p1",
                platform="Darwin"
            )
            
            writer.write_sync(session)
            
            # Check file exists
            session_file = Path(tmpdir) / "session.json"
            assert session_file.exists()
            
            # Check content
            with open(session_file) as f:
                data = json.load(f)
                assert data["game_name"] == "Test Game"
                assert data["start_time"] == 1000
                assert data["participant_id"] == "p1"
