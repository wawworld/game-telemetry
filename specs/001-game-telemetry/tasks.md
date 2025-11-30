---
description: "Task breakdown for game-agnostic telemetry system implementation"
---

# Tasks: Game-Agnostic Telemetry System

**Input**: Design documents from `/specs/001-game-telemetry/`
**Prerequisites**: plan.md ✅, spec.md ✅, input-capture-research.md ✅

**Tests**: No test tasks included - tests not explicitly requested in feature specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project structure**: `src/`, `tests/` at repository root
- Follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure (src/, tests/, configs/, docs/)
- [ ] T002 Initialize Python project with pyproject.toml (Python 3.11+, dependencies: pynput, PyYAML, Pillow, opencv-python, pytest)
- [ ] T003 [P] Create .gitignore for Python project (venv/, __pycache__/, *.pyc, data/, logs/)
- [ ] T004 [P] Setup pytest configuration in pyproject.toml or pytest.ini
- [ ] T005 [P] Create README.md with project overview and installation instructions
- [ ] T006 [P] Create LICENSE file (if applicable)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create base data models module in src/models/__init__.py (empty package)
- [ ] T008 [P] Create telemetry event model in src/models/event.py (TelemetryEvent dataclass: timestamp, event_type, parameters, game_id, session_id)
- [ ] T009 [P] Create screen capture model in src/models/frame.py (Frame dataclass: timestamp, image_path, session_id)
- [ ] T010 [P] Create game configuration model in src/models/config.py (GameConfig dataclass: game_name, roi_detection, session_triggers, capture_settings)
- [ ] T011 [P] Create collection session model in src/models/session.py (Session dataclass: session_id, start_time, end_time, participant_id, game_metadata)
- [ ] T012 Create base services module in src/services/__init__.py (empty package)
- [ ] T013 Create utilities module in src/utils/__init__.py with timestamp helper functions (unix_timestamp_ms, iso8601_timestamp)
- [ ] T014 [P] Create configuration loader service in src/services/config_loader.py (load YAML/JSON configs, validate structure)
- [ ] T015 [P] Create data writer service base in src/services/data_writer.py (abstract interface for event/frame/metadata writing)
- [ ] T016 [P] Create event buffer implementation in src/services/event_buffer.py (thread-safe in-memory buffer with async flush)
- [ ] T017 Create error handling and logging infrastructure in src/utils/logging.py (setup logging to console and file)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Initial Telemetry Setup for New Game (Priority: P1) 🎯 MVP

**Goal**: Enable researchers to collect player behavior data from a single game using configuration files without game modification

**Independent Test**: Configure a single game with minimal settings (game name, process identification), run the game, perform keyboard/mouse actions, verify that input events are captured with accurate timestamps and stored to local files in JSON Lines format

### Implementation for User Story 1

- [ ] T018 [P] [US1] Implement JSON Lines event writer in src/services/writers/event_writer.py (write events incrementally, one per line)
- [ ] T019 [P] [US1] Implement JSON metadata writer in src/services/writers/metadata_writer.py (write session metadata as single JSON file)
- [ ] T020 [P] [US1] Implement screen capture writer in src/services/writers/frame_writer.py (save frames as JPEG/PNG with timestamp in filename: frame_<unix_timestamp_ms>.jpg)
- [ ] T021 [US1] Implement input capture service using pynput in src/services/input_capture.py (keyboard listener, mouse listener, timestamp on event callback, forward to event buffer)
- [ ] T022 [US1] Implement screen capture service in src/services/screen_capture.py (capture full screen at configurable FPS using Pillow, timestamp each frame, forward to frame writer)
- [ ] T023 [US1] Implement game process detection service in src/services/game_detector.py (detect running game by process name or window title)
- [ ] T024 [US1] Implement session manager service in src/services/session_manager.py (create session, start/stop collection, generate session ID, coordinate services)
- [ ] T025 [US1] Create main telemetry controller in src/telemetry_controller.py (orchestrate config loading, service initialization, session lifecycle)
- [ ] T026 [US1] Create CLI entry point in src/cli/main.py (start/stop commands, config file path argument, basic status output)
- [ ] T027 [US1] Add graceful shutdown handling in src/telemetry_controller.py (flush buffers, close listeners, finalize session metadata)
- [ ] T028 [US1] Create sample configuration file in configs/sample_game.yaml (example game profile with minimal required fields)

**Checkpoint**: At this point, User Story 1 should be fully functional - researchers can configure and collect telemetry from a single game

---

## Phase 4: User Story 2 - Adding Multiple Games with Minimal Configuration (Priority: P2)

**Goal**: Allow researchers to configure multiple games and have the system automatically apply the correct settings based on which game is currently running

**Independent Test**: Configure 2-3 different games with distinct identification parameters (e.g., game A by window title, game B by process name, game C by executable path), run them in sequence, verify that each game's data is collected into separate directories without data mixing

### Implementation for User Story 2

- [ ] T029 [P] [US2] Extend game detector service in src/services/game_detector.py to support multiple game profiles (match against list of configs, return matched config)
- [ ] T030 [US2] Update session manager in src/services/session_manager.py to create game-specific output directories (data/<game_name>/<session_id>/)
- [ ] T031 [US2] Extend telemetry controller in src/telemetry_controller.py to hot-reload configurations when active game changes
- [ ] T032 [US2] Update CLI in src/cli/main.py to support multiple config files (accept multiple --config arguments or config directory path)
- [ ] T033 [US2] Create multi-game configuration examples in configs/ (multiple YAML files demonstrating different identification methods)
- [ ] T034 [US2] Add game identification metadata to session metadata in src/services/writers/metadata_writer.py (include game_name, detection_method)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - multi-game support is operational

---

## Phase 5: User Story 3 - Validating Data Quality and Completeness (Priority: P2)

**Goal**: Ensure collected telemetry data is accurate, complete, and suitable for research analysis

**Independent Test**: Perform a scripted sequence of actions (e.g., 10 clicks at known positions with known timing), examine output files, verify all 10 events are present with timestamps within acceptable tolerance (10ms) and correct position parameters

### Implementation for User Story 3

- [ ] T035 [P] [US3] Add event capture rate monitoring to input capture service in src/services/input_capture.py (track events received vs events written)
- [ ] T036 [US3] Implement timestamp accuracy validation in src/utils/timestamp_validator.py (compare event timestamp to system time at capture, log discrepancies)
- [ ] T037 [US3] Add data completeness checks to session manager in src/services/session_manager.py (verify all buffered events flushed before session close)
- [ ] T038 [US3] Implement event-to-frame synchronization validator in src/utils/sync_validator.py (check average sync accuracy between events and nearest frame timestamp)
- [ ] T039 [US3] Add validation reporting to CLI in src/cli/main.py (display capture rate, timestamp accuracy, sync accuracy after session ends)
- [ ] T040 [US3] Create data quality validation script in src/scripts/validate_session.py (standalone script to analyze collected session data and report quality metrics)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should work independently - data quality validation is operational

---

## Phase 6: User Story 4 - Automatic Session Detection and Management (Priority: P2)

**Goal**: Automatically detect when a configured game starts (via reference image matching) and begin data collection without manual intervention

**Independent Test**: Provide a reference screenshot of gameplay, start the game, verify that the system automatically begins collecting input events and screen captures when the game window matches the reference image, without requiring manual start command

### Implementation for User Story 4

- [ ] T041 [P] [US4] Create ROI detection module in src/services/roi_detection.py (template matching using OpenCV or similar, configurable similarity threshold 0.85-0.90)
- [ ] T042 [P] [US4] Create region of interest model in src/models/roi.py (ROI dataclass: x, y, width, height, detection_confidence, last_updated)
- [ ] T043 [US4] Implement automatic game start detection in src/services/game_detector.py (periodic screen capture, compare against reference images, trigger on match)
- [ ] T044 [US4] Update screen capture service in src/services/screen_capture.py to support ROI-only capture (crop to detected region before saving)
- [ ] T045 [US4] Extend session manager in src/services/session_manager.py with automatic session triggers (start on image match, end on keyboard command/timeout/inactivity)
- [ ] T046 [US4] Add ROI re-detection logic to screen capture service in src/services/screen_capture.py (periodic re-detection at configurable interval, default 5.0s)
- [ ] T047 [US4] Implement ROI detection retry with fallback in src/services/roi_detection.py (retry at configurable intervals when detection fails, pause collection until success)
- [ ] T048 [US4] Add manual ROI override command to CLI in src/cli/main.py (force immediate re-detection on user request)
- [ ] T049 [US4] Extend game configuration model in src/models/config.py to include ROI detection settings (reference_images, match_threshold, padding, update_interval, manual_fallback_coords)
- [ ] T050 [US4] Create sample configuration with ROI detection in configs/game_with_roi_detection.yaml (example with reference images and detection parameters)

**Checkpoint**: At this point, User Stories 1-4 should work independently - automatic session detection is operational

---

## Phase 7: User Story 5 - Long-Duration Session Recording (Priority: P3)

**Goal**: Support extended gameplay sessions (3+ hours) with minimal performance impact and no data loss

**Independent Test**: Run a game session for 2-4 hours with active telemetry collection, monitor system resource usage (CPU, memory, disk), verify game performance remains stable (no noticeable lag) and all data is captured without loss

### Implementation for User Story 5

- [ ] T051 [P] [US5] Add performance monitoring to telemetry controller in src/telemetry_controller.py (track CPU %, memory usage, buffer size)
- [ ] T052 [US5] Optimize event buffer implementation in src/services/event_buffer.py (tune buffer size, flush frequency to reduce overhead)
- [ ] T053 [US5] Implement incremental file writing in src/services/writers/event_writer.py (immediate writes without accumulating in memory)
- [ ] T054 [US5] Add disk space monitoring to session manager in src/services/session_manager.py (check available space before writing, warn if low)
- [ ] T055 [US5] Optimize screen capture performance in src/services/screen_capture.py (reduce image quality if needed to maintain target FPS)
- [ ] T056 [US5] Add session duration limits to configuration in src/models/config.py (max_duration_seconds, auto-stop when reached)
- [ ] T057 [US5] Create performance profiling script in src/scripts/profile_telemetry.py (measure CPU/memory overhead during typical session)

**Checkpoint**: All user stories should now be independently functional - long-duration recording is operational

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T058 [P] Create comprehensive user documentation in docs/user_guide.md (installation, configuration, usage examples)
- [ ] T059 [P] Create developer documentation in docs/developer_guide.md (architecture overview, adding new features)
- [ ] T060 [P] Add configuration validation to config loader in src/services/config_loader.py (validate required fields, check image paths exist, validate threshold ranges)
- [ ] T061 [P] Create example configurations for common games in configs/examples/ (at least 3 different game types)
- [ ] T062 Code cleanup and refactoring (remove debug code, improve naming consistency, add docstrings)
- [ ] T063 [P] Add error handling edge cases (game crash detection, disk full handling, corrupted config files)
- [ ] T064 Performance optimization across all stories (profile and optimize bottlenecks if needed)
- [ ] T065 Security hardening (input validation, safe file operations, permission checks)
- [ ] T066 [P] Create quickstart validation script based on quickstart.md scenarios (if quickstart.md exists)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T006) - **BLOCKS all user stories**
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion (T007-T017)
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P2 → P3)
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Phase 3**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2) - Phase 4**: Can start after Foundational (Phase 2) - Extends US1 components but independently testable
- **User Story 3 (P2) - Phase 5**: Can start after Foundational (Phase 2) - Adds validation to US1 components but independently testable
- **User Story 4 (P2) - Phase 6**: Can start after Foundational (Phase 2) - Adds automatic detection to US1 components but independently testable
- **User Story 5 (P3) - Phase 7**: Can start after Foundational (Phase 2) - Optimizes US1 components but independently testable

### Within Each User Story

- **US1**: Event/frame/metadata writers can be parallel (T018-T020) → input capture (T021) and screen capture (T022) in parallel → services integration (T023-T027) → finalization (T028)
- **US2**: Game detector extension (T029) before controller update (T031) → other tasks in parallel
- **US3**: All validation tasks (T035-T038) can run in parallel → reporting (T039-T040)
- **US4**: ROI model and detection can be parallel (T041-T042) → detector update (T043) before screen capture update (T044) → other tasks follow
- **US5**: Performance monitoring and optimization tasks largely independent (T051-T057)

### Parallel Opportunities

- **Setup (Phase 1)**: T003, T004, T005, T006 can run in parallel after T001-T002
- **Foundational (Phase 2)**: T008, T009, T010, T011 (models) in parallel → T014, T015, T016 (services) in parallel after T012-T013
- **User Story 1**: T018, T019, T020 in parallel → T021, T022 in parallel → rest sequential
- **User Story 2**: T029, T033, T034 can run in parallel → T030-T032 after T029
- **User Story 3**: T035, T036, T037, T038 can run in parallel → T039, T040 after validation tasks
- **User Story 4**: T041, T042, T049, T050 can run in parallel → rest sequential
- **User Story 5**: T051, T052, T053, T054, T055, T056 can run in parallel → T057
- **Polish (Phase 8)**: T058, T059, T060, T061, T063, T066 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all writers for User Story 1 together:
Task T018: "Implement JSON Lines event writer in src/services/writers/event_writer.py"
Task T019: "Implement JSON metadata writer in src/services/writers/metadata_writer.py"
Task T020: "Implement screen capture writer in src/services/writers/frame_writer.py"

# Then launch capture services together:
Task T021: "Implement input capture service using pynput in src/services/input_capture.py"
Task T022: "Implement screen capture service in src/services/screen_capture.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T017) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T018-T028)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Can you configure a game and collect telemetry data?
   - Are events captured with accurate timestamps?
   - Are files written in correct formats?
5. Deploy/demo if ready

**Estimated MVP Scope**: ~28 tasks, focusing on core telemetry collection functionality

### Incremental Delivery

1. **Foundation** (Setup + Foundational) → Foundation ready
2. **MVP** (Add User Story 1) → Test independently → Deploy/Demo - Basic telemetry works!
3. **Multi-Game** (Add User Story 2) → Test independently → Deploy/Demo - Multiple games supported!
4. **Data Quality** (Add User Story 3) → Test independently → Deploy/Demo - Validation added!
5. **Automation** (Add User Story 4) → Test independently → Deploy/Demo - Auto-detection works!
6. **Performance** (Add User Story 5) → Test independently → Deploy/Demo - Long sessions supported!
7. **Polish** (Phase 8) → Final refinements

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T017)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T018-T028) - MVP
   - **Developer B**: User Story 2 (T029-T034) - Multi-game support
   - **Developer C**: User Story 3 (T035-T040) - Validation
3. Then:
   - **Developer A**: User Story 4 (T041-T050) - Automation
   - **Developer B**: User Story 5 (T051-T057) - Performance
   - **Developer C**: Polish (T058-T066) - Documentation & hardening
4. Stories complete and integrate independently

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] label**: Maps task to specific user story for traceability (US1, US2, US3, US4, US5)
- **No tests**: Tests not included as they weren't explicitly requested in specification
- **Each user story should be independently completable and testable**: Avoid cross-story dependencies that break independence
- **Commit after each task or logical group**: Maintain clean git history
- **Stop at any checkpoint to validate story independently**: Ensure each story works before moving to next
- **Avoid vague tasks**: Each task has specific file path and clear action
- **rdev migration**: Plan includes pynput for MVP (Phase 3), future migration to rdev for production optimization (not in current task list)

---

## Summary

- **Total Tasks**: 66 tasks across 8 phases
- **MVP Scope**: Phases 1-3 (28 tasks) - User Story 1 only
- **Full Feature**: Phases 1-7 (57 tasks) - All user stories
- **Polish**: Phase 8 (9 tasks) - Documentation and hardening
- **Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phases
- **Independent Stories**: Each user story (US1-US5) can be tested independently after Foundational phase
- **Critical Path**: Setup → Foundational (BLOCKS) → User Stories (P1 → P2s → P3) → Polish
