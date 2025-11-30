"""Unit tests for data models."""

import pytest
from datetime import datetime
from models.event import TelemetryEvent
from models.frame import Frame
from models.session import Session
from models.roi import ROI
from models.config import GameConfig, ROIDetectionConfig, SessionTrigger, CaptureSettings


class TestTelemetryEvent:
    """Test TelemetryEvent model."""
    
    def test_create_keyboard_event(self):
        """Test creating a keyboard event."""
        event = TelemetryEvent(
            timestamp=1234567890123,
            event_type="keyboard_press",
            game_id="test_game",
            session_id="test_session",
            parameters={"key": "a"}
        )
        
        assert event.timestamp == 1234567890123
        assert event.event_type == "keyboard_press"
        assert event.game_id == "test_game"
        assert event.session_id == "test_session"
        assert event.parameters["key"] == "a"
    
    def test_to_dict(self):
        """Test converting event to dictionary."""
        event = TelemetryEvent(
            timestamp=1234567890123,
            event_type="mouse_click",
            game_id="game",
            session_id="session",
            parameters={"button": "left", "x": 100, "y": 200}
        )
        
        result = event.to_dict()
        
        assert result["timestamp"] == 1234567890123
        assert result["event_type"] == "mouse_click"
        assert result["game_id"] == "game"
        assert result["session_id"] == "session"
        assert result["parameters"]["button"] == "left"
        assert result["parameters"]["x"] == 100
        assert result["parameters"]["y"] == 200
    
    def test_from_dict(self):
        """Test creating event from dictionary."""
        data = {
            "timestamp": 1234567890123,
            "event_type": "keyboard_release",
            "game_id": "game",
            "session_id": "session",
            "parameters": {"key": "escape"}
        }
        
        event = TelemetryEvent.from_dict(data)
        
        assert event.timestamp == 1234567890123
        assert event.event_type == "keyboard_release"
        assert event.game_id == "game"
        assert event.session_id == "session"
        assert event.parameters["key"] == "escape"


class TestROI:
    """Test ROI model."""
    
    def test_create_roi(self):
        """Test creating ROI."""
        roi = ROI(x=100, y=200, width=800, height=600)
        
        assert roi.x == 100
        assert roi.y == 200
        assert roi.width == 800
        assert roi.height == 600
    
    def test_bounds_property(self):
        """Test bounds tuple property."""
        roi = ROI(x=10, y=20, width=300, height=400)
        
        bounds = roi.bounds
        
        # bounds returns (x, y, x+width, y+height)
        assert bounds == (10, 20, 310, 420)
        assert isinstance(bounds, tuple)


class TestSession:
    """Test Session model."""
    
    def test_create_session(self):
        """Test creating a session."""
        session = Session(
            game_name="Test Game",
            start_time=1234567890000,
            participant_id="participant_001",
            platform="Darwin"
        )
        
        assert session.game_name == "Test Game"
        assert session.start_time == 1234567890000
        assert session.participant_id == "participant_001"
        assert session.platform == "Darwin"
        assert session.end_time is None
        assert session.game_version is None
        assert isinstance(session.metadata, dict)
    
    def test_session_id_generation(self):
        """Test that session_id is automatically generated as UUID."""
        session1 = Session(
            game_name="Game",
            start_time=1000,
            platform="Darwin"
        )
        session2 = Session(
            game_name="Game",
            start_time=1000,
            platform="Darwin"
        )
        
        # Each session should have unique UUID
        assert session1.session_id != session2.session_id
        assert len(session1.session_id) == 36  # UUID format
        assert "-" in session1.session_id
    
    def test_to_dict(self):
        """Test converting session to dictionary."""
        session = Session(
            game_name="Test",
            start_time=1000,
            participant_id="p1",
            platform="Darwin"
        )
        session.end_time = 2000
        session.game_version = "1.0.0"
        session.metadata["custom_field"] = "value"
        
        result = session.to_dict()
        
        assert result["game_name"] == "Test"
        assert result["start_time"] == 1000
        assert result["end_time"] == 2000
        assert result["participant_id"] == "p1"
        assert result["game_version"] == "1.0.0"
        assert result["platform"] == "Darwin"
        assert result["metadata"]["custom_field"] == "value"


class TestGameConfig:
    """Test GameConfig model."""
    
    def test_create_minimal_config(self):
        """Test creating config with minimal required fields."""
        config = GameConfig(
            game_name="Test Game",
            process_name="test.exe",
            capture_settings=CaptureSettings(
                frame_rate=15,
                image_format="jpeg",
                image_quality=85,
                enabled_event_types=["keyboard_press", "mouse_click"]
            ),
            output_directory="data/test"
        )
        
        assert config.game_name == "Test Game"
        assert config.process_name == "test.exe"
        assert config.capture_settings.frame_rate == 15
        assert config.output_directory == "data/test"
        assert config.window_title is None
        assert config.executable_path is None
    
    def test_create_full_config(self):
        """Test creating config with all fields."""
        roi_config = ROIDetectionConfig(
            enabled=True,
            reference_images=["ref1.png", "ref2.png"],
            match_threshold=0.875,
            padding=10,
            update_interval_seconds=5.0,
            retry_interval_seconds=5.0,
            manual_fallback_coords=ROI(x=0, y=0, width=1920, height=1080)
        )
        
        triggers = [
            SessionTrigger(type="manual", parameters={}),
            SessionTrigger(type="keyboard", parameters={"key": "F9"})
        ]
        
        capture = CaptureSettings(
            frame_rate=30,
            image_format="png",
            image_quality=95,
            enabled_event_types=["keyboard_press", "keyboard_release", "mouse_click"]
        )
        
        config = GameConfig(
            game_name="Full Game",
            process_name="game.exe",
            window_title="Game Window",
            executable_path="/usr/bin/game",
            roi_detection=roi_config,
            session_start_triggers=triggers,
            session_end_triggers=triggers,
            capture_settings=capture,
            output_directory="data/full"
        )
        
        assert config.game_name == "Full Game"
        assert config.process_name == "game.exe"
        assert config.window_title == "Game Window"
        assert config.executable_path == "/usr/bin/game"
        assert config.roi_detection.enabled is True
        assert len(config.roi_detection.reference_images) == 2
        assert len(config.session_start_triggers) == 2
        assert config.capture_settings.frame_rate == 30


class TestCaptureSettings:
    """Test CaptureSettings model."""
    
    def test_default_settings(self):
        """Test default capture settings."""
        settings = CaptureSettings(
            frame_rate=15,
            image_format="jpeg",
            image_quality=85,
            enabled_event_types=["keyboard_press"]
        )
        
        assert settings.frame_rate == 15
        assert settings.image_format == "jpeg"
        assert settings.image_quality == 85
        assert "keyboard_press" in settings.enabled_event_types
    
    def test_all_event_types(self):
        """Test with all event types enabled."""
        all_types = [
            "keyboard_press",
            "keyboard_release",
            "mouse_click",
            "mouse_move",
            "mouse_scroll"
        ]
        
        settings = CaptureSettings(
            frame_rate=30,
            image_format="png",
            image_quality=100,
            enabled_event_types=all_types
        )
        
        assert len(settings.enabled_event_types) == 5
        assert "keyboard_press" in settings.enabled_event_types
        assert "mouse_scroll" in settings.enabled_event_types
