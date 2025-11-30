# Game-Agnostic Telemetry System

A non-intrusive telemetry system for collecting player behavior data from multiple games without source code modification.

## Features

- **Game-Agnostic**: Works with any game through process detection and screen monitoring
- **Non-Intrusive**: No game modification required - uses system-level input capture
- **Configurable**: YAML/JSON configuration files for per-game customization
- **Automatic Detection**: Template matching for ROI detection and automatic session management
- **High Performance**: <5% CPU overhead, <100MB memory footprint
- **Cross-Platform**: Windows, macOS, and Linux support

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd spec-kit-project
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
pip install -e ".[dev]"  # For development dependencies
```

## Quick Start

### 1. Configure a Game

Create a configuration file in `configs/` (e.g., `configs/my_game.yaml`):

```yaml
game_name: "MyGame"
process_name: "mygame.exe"  # Or use window_title: "My Game Window"

capture_settings:
  frame_rate: 15
  image_format: "jpeg"
  image_quality: 85

session_triggers:
  start:
    - type: "manual"
  end:
    - type: "keyboard"
      key: "F9"
    - type: "timeout"
      duration_seconds: 3600  # 1 hour max

output_directory: "data/my_game"
```

### 2. Start Data Collection

```bash
game-telemetry start --config configs/my_game.yaml
```

### 3. Stop Data Collection

```bash
game-telemetry stop
```

Or press the configured stop key (e.g., F9).

### 4. View Collected Data

Data is stored in the configured output directory:
- `events.jsonl` - Player input events (JSON Lines format)
- `session.json` - Session metadata
- `frame_<timestamp>.jpg` - Screen captures

## Configuration

See `configs/sample_game.yaml` for a complete configuration example with all available options.

### Key Configuration Options

- **Game Identification**: `process_name`, `window_title`, or `executable_path`
- **ROI Detection**: Template matching with reference images
- **Session Triggers**: Automatic start/stop based on various conditions
- **Capture Settings**: Frame rate, image quality, event types
- **Performance**: Buffer sizes, async I/O settings

## Architecture

```
src/
├── models/              # Data models (Event, Frame, Session, Config, ROI)
├── services/            # Core services (capture, detection, writing)
├── cli/                 # Command-line interface
├── utils/               # Utilities (logging, validation)
└── telemetry_controller.py  # Main orchestrator
```

## Development

### Running Tests

```bash
pytest                    # Run all tests
pytest tests/unit         # Run unit tests only
pytest tests/integration  # Run integration tests only
pytest --cov=src          # Run with coverage
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
pylint src/

# Type checking
mypy src/
```

## Performance Goals

- **CPU Overhead**: <5% during active capture
- **Memory Footprint**: <100MB
- **Event Capture Rate**: 99.9% of all input events
- **Timestamp Accuracy**: ±10ms for events, ±20ms for sync
- **Long Sessions**: 4+ hours without data loss

## Documentation

- [User Guide](docs/user_guide.md) - Detailed usage instructions
- [Developer Guide](docs/developer_guide.md) - Architecture and development
- [Specification](specs/001-game-telemetry/spec.md) - Feature specification
- [Implementation Plan](specs/001-game-telemetry/plan.md) - Technical design

## License

[Specify your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information here]
