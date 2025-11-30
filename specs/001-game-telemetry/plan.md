# Implementation Plan: Game-Agnostic Telemetry System

**Branch**: `001-game-telemetry` | **Date**: 2025-11-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-game-telemetry/spec.md`

## Summary

Develop a game-agnostic telemetry system that non-intrusively collects player behavior data from multiple games without source code modification. The system uses Python with pynput for MVP input capture (with future rdev migration for production optimization), template matching for ROI detection, and structured configuration files (YAML/JSON) for per-game customization.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+
**Primary Dependencies**: 
- Input capture: pynput (MVP/Phase 3) → rdev with PyO3 bindings (future production optimization)
- Screen capture: Pillow (PIL)
- Template matching: OpenCV (cv2) for ROI detection
- Config parser: PyYAML
- Async I/O: asyncio
**Storage**: Local file system (JSON Lines for events, JPEG/PNG for frames, JSON for metadata)
**Testing**: pytest
**Target Platform**: Windows/macOS/Linux desktop environments
**Project Type**: single (background service/daemon)
**Performance Goals**: 
- <5% CPU overhead during active capture (spec FR-017)
- <100MB memory footprint (spec FR-018)
- 99.9% event capture rate (spec FR-019)
- 10ms timestamp accuracy for events (spec FR-020)
- 20ms synchronization accuracy for frames (spec clarification #8)
- 15 FPS screen capture default (spec FR-005)
**Constraints**: 
- Non-intrusive operation (spec principle #2)
- No game modification required (spec principle #1)
- Cross-platform compatibility (spec dependencies)
- Configuration-driven design (spec clarification #7)
**Scale/Scope**: 
- Support multiple concurrent game sessions
- Handle 100+ input events per second
- Template matching against 5-10 ROIs per check
- Session durations up to several hours
- File I/O for thousands of frames per session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/              # Data models (Event, Frame, Session, Config, ROI)
│   ├── __init__.py
│   ├── event.py
│   ├── frame.py
│   ├── config.py
│   ├── session.py
│   └── roi.py
├── services/            # Core services
│   ├── __init__.py
│   ├── config_loader.py
│   ├── data_writer.py
│   ├── event_buffer.py
│   ├── input_capture.py
│   ├── screen_capture.py
│   ├── game_detector.py
│   ├── session_manager.py
│   ├── roi_detection.py
│   └── writers/
│       ├── event_writer.py
│       ├── metadata_writer.py
│       └── frame_writer.py
├── cli/                 # Command-line interface
│   └── main.py
├── utils/               # Utilities
│   ├── __init__.py
│   ├── logging.py
│   ├── timestamp_validator.py
│   └── sync_validator.py
├── scripts/             # Standalone scripts
│   ├── validate_session.py
│   └── profile_telemetry.py
└── telemetry_controller.py  # Main orchestrator

tests/
├── unit/                # Unit tests (if added later)
├── integration/         # Integration tests (if added later)
└── contract/            # Contract tests (if added later)

configs/                 # Configuration files
├── sample_game.yaml
├── game_with_roi_detection.yaml
└── examples/

docs/                    # Documentation
├── user_guide.md
└── developer_guide.md

data/                    # Telemetry output (gitignored)
└── <game_name>/
    └── <session_id>/
```

**Structure Decision**: Single project layout selected. This is a standalone background service/daemon with no frontend, backend separation, or mobile components. All code resides in `src/` with clear separation by concern (models, services, CLI, utils).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
