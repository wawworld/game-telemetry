# Feature Specification: Game-Agnostic Telemetry System

**Feature Branch**: `001-game-telemetry`  
**Created**: 2025-11-30  
**Status**: Draft  
**Input**: User description: "다양한 게임에서 플레이어의 행동 데이터를 비침투적으로 수집하여, 게임 분석 및 연구에 활용할 수 있는 범용 텔레메트리 시스템 개발"

## Clarifications

### Session 2025-11-30

- Q: Template matching sensitivity for game/ROI detection → A: Moderate matching (85-90% similarity threshold)
- Q: ROI detection fallback strategy when automatic detection fails → A: Retry detection periodically while pausing collection
- Q: Session auto-start trigger logic when multiple triggers configured → A: Start on first trigger that activates (OR logic)
- Q: Participant ID anonymization method → A: One-way hash of original ID
- Q: Default screen capture frame rate when not specified → A: 15 FPS
- Q: Configuration flexibility for game profiles → A: Support structured configuration files (YAML/JSON) with per-game customization of ROI detection, session triggers, capture settings, avoiding hardcoded values
- Q: Frame timestamp storage and correlation efficiency → A: Store Unix timestamps in image filenames (frame_<unix_timestamp_ms>.jpg) for O(1) temporal lookups
- Q: Synchronization accuracy and trigger check frequencies → A: 20ms average sync accuracy; start triggers check at 1.0s intervals (0.5-5.0s range), end triggers per-frame, ROI re-detection at 5.0s (configurable)
- Q: ROI detection retry and manual control → A: Configurable retry intervals (default 5s), support manual override to force immediate re-detection

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initial Telemetry Setup for New Game (Priority: P1)

A game researcher wants to start collecting player behavior data from a game without modifying the game's source code. They configure the telemetry system by providing game-specific observation settings (e.g., window title, process name, screen region parameters), and the system begins collecting event data immediately.

**Why this priority**: This is the core value proposition - enabling non-intrusive data collection. Without this, the system cannot function.

**Independent Test**: Can be fully tested by configuring a single game with minimal settings and verifying that player action events (keyboard, mouse, screen changes) are captured with accurate timestamps and stored to a local data file.

**Acceptance Scenarios**:

1. **Given** a game is running and the telemetry system is not yet configured, **When** the researcher creates a game configuration file (YAML/JSON) with ROI detection settings, session triggers, and capture parameters, **Then** the system begins observing and recording player input events and screen captures according to the specified settings
2. **Given** the telemetry system is configured for a game with custom thresholds and frame rates, **When** a player performs actions (clicks, key presses, mouse movements), **Then** each event is recorded with precise timestamp, event type, relevant parameters, and synchronized with screen capture frames at the configured rate
3. **Given** the game session ends via any configured end trigger (keyboard, timeout, or inactivity), **When** the researcher accesses the data collection folder, **Then** all recorded events, screen captures, and session metadata are available in structured formats

---

### User Story 2 - Adding Multiple Games with Minimal Configuration (Priority: P2)

A researcher working with multiple games wants to extend telemetry coverage to additional titles. They add new game configurations by specifying only the essential identification parameters, and the system automatically handles each game independently without conflicts.

**Why this priority**: Demonstrates extensibility - a key design principle. Shows the system scales beyond a single game.

**Independent Test**: Can be tested by configuring 2-3 different games with distinct identification parameters, running them in sequence or in parallel, and verifying that each game's telemetry data is collected separately without data mixing or system conflicts.

**Acceptance Scenarios**:

1. **Given** one game is already configured, **When** the researcher adds a second game configuration with different identification parameters, **Then** the system recognizes both games and collects data for whichever is currently running
2. **Given** multiple games are configured, **When** the researcher switches between running different games, **Then** the telemetry system automatically detects which game is active and applies the correct observation settings
3. **Given** two different games are configured, **When** reviewing collected data, **Then** each game's data is stored in separate, clearly labeled datasets

---

### User Story 3 - Validating Data Quality and Completeness (Priority: P2)

A researcher wants to ensure that collected telemetry data is accurate and complete for their analysis needs. They review the captured events, verify timestamps are precise, and confirm that no events were missed during critical gameplay moments.

**Why this priority**: Data quality is essential for research validity. Poor quality data renders the system useless for analysis.

**Independent Test**: Can be tested by performing a scripted sequence of actions in a game (e.g., 10 specific clicks in known positions with known timing), then verifying that all 10 events were captured with correct timestamps (within acceptable tolerance like 10ms) and correct parameters.

**Acceptance Scenarios**:

1. **Given** a game session is being recorded, **When** performing a rapid sequence of player actions, **Then** all actions are captured without any events being dropped
2. **Given** a recorded session with known events, **When** examining event timestamps, **Then** timestamps are accurate within 10 milliseconds of actual occurrence
3. **Given** a game session with both frequent and rare player actions, **When** analyzing the collected data, **Then** both common actions (movement) and rare actions (menu interactions) are captured completely

---

### User Story 4 - Automatic Session Detection and Management (Priority: P2)

A researcher wants the telemetry system to automatically detect when a game starts and begin recording without manual intervention. They provide a reference screenshot of the game's typical gameplay screen, and the system monitors for this pattern to trigger automatic data collection.

**Why this priority**: Automation reduces human error and ensures consistent data collection. Critical for unattended recording scenarios.

**Independent Test**: Can be tested by providing a reference game screenshot, starting the game, and verifying that the system automatically begins collecting input events and screen captures when the game window matches the reference image, without requiring manual start commands.

**Acceptance Scenarios**:

1. **Given** a reference game screenshot is provided in the configuration, **When** the game window appears and matches the reference image, **Then** the telemetry system automatically begins data collection
2. **Given** data collection is running automatically, **When** the researcher sends a stop command or configured time limit is reached, **Then** the session ends and all data is finalized
3. **Given** multiple games are configured with different reference images, **When** any configured game starts, **Then** the system detects the correct game and applies the appropriate collection settings

---

### User Story 5 - Long-Duration Session Recording (Priority: P3)

A researcher needs to collect telemetry data from extended gameplay sessions lasting several hours. The system continues recording throughout the entire session with minimal performance impact on the game or the player's computer.

**Why this priority**: Enables realistic research scenarios but is less critical than basic functionality and data quality.

**Independent Test**: Can be tested by running a game session for 2-4 hours with active telemetry collection, monitoring system resource usage (CPU, memory, disk), and verifying that game performance remains stable and all data is captured without loss.

**Acceptance Scenarios**:

1. **Given** a long gameplay session (3+ hours), **When** telemetry collection is running, **Then** system overhead remains below 5% CPU and 100MB memory usage
2. **Given** a multi-hour recording session, **When** the session completes, **Then** all data is successfully written to storage without corruption or data loss
3. **Given** telemetry is running during an extended session, **When** the player monitors game performance, **Then** the game's frame rate and responsiveness are not noticeably affected

---

### Edge Cases

- What happens when the target game process terminates unexpectedly (crash) during data collection?
- How does the system handle extremely rapid input events (e.g., 100+ mouse movements per second)?
- What occurs when disk storage becomes full during an active recording session?
- How does the system behave when multiple instances of the same game are running simultaneously?
- What happens when the game's window title or process name changes during gameplay (e.g., level transitions that update window title)?
- How does the system handle games running in fullscreen vs windowed mode?
- What occurs if the system's configuration file is modified while data collection is active?
- How does the system handle reference images that partially match multiple different game states?
- What happens when screen capture frame rate cannot keep up with configured rate due to system load?
- How does the system behave when the game window is obscured or minimized during recording?
- What is the retry interval for ROI detection when automatic detection fails, and can it be configured?
- How does the system validate game configuration files for correctness (valid thresholds, existing image paths, etc.)?
- What happens when a configuration references non-existent reference images?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST observe player input events (keyboard, mouse) from target game processes without requiring game source code modifications
- **FR-002**: System MUST identify and attach to target game processes using configurable identification parameters (process name, window title, or executable path)
- **FR-003**: System MUST capture event timestamps with millisecond precision or better
- **FR-004**: System MUST record the following event types at minimum: keyboard key presses/releases (with key codes), mouse button clicks, mouse position changes, and mouse scroll events
- **FR-004a**: System MUST capture screen images at a configurable frame rate throughout the recording session
- **FR-004b**: System MUST automatically detect and extract the game region from the full screen using template matching with user-provided reference images (default similarity threshold: 85-90% for moderate matching, configurable per game)
- **FR-004c**: System MUST retry ROI detection periodically when automatic detection fails, pausing data collection until successful detection or manual intervention
- **FR-005**: System MUST allow researchers to add new game configurations through a simple configuration file or interface without system recompilation
- **FR-005a**: System MUST support structured configuration files (YAML or JSON format) containing game-specific settings including ROI detection parameters (reference images, match thresholds, padding, update intervals), manual ROI fallback coordinates, multiple session triggers (image-based, timeout-based, keyboard-based, inactivity-based), and capture settings (frame rate, image quality)
- **FR-006**: System MUST store input event data in JSON Lines format (one event per line), session metadata in JSON format, and screen captures as individual image files (JPEG or PNG) with Unix timestamp in milliseconds embedded in filename (format: frame_<unix_timestamp_ms>.jpg) to enable efficient event-to-frame correlation without loading all images
- **FR-006a**: System MUST use consistent timestamp formats (ISO 8601 or Unix epoch in milliseconds) across all data types
- **FR-007**: System MUST separate data collection for different games into distinct datasets with clear game identification
- **FR-008**: System MUST maintain data collection during the entire game session from game launch to termination
- **FR-009**: System MUST handle collection failures gracefully without crashing the target game
- **FR-010**: System MUST provide a mechanism to start and stop data collection independent of game execution
- **FR-011**: System MUST operate with minimal performance impact on the target game (target: <5% CPU overhead, <100MB memory)
- **FR-012**: System MUST prevent data loss by buffering events and ensuring writes complete successfully
- **FR-013**: System MUST include game identification metadata with each collected event (game name, session ID, game version if detectable)
- **FR-014**: System MUST detect when a configured game starts by comparing current screen content against reference images using template matching, and automatically begin collection when a match is found (if auto-start is enabled); when multiple start triggers are configured, system MUST begin session when any trigger activates (OR logic)
- **FR-014a**: System MUST support multiple configurable session end triggers including keyboard commands, timeout duration limits, and inactivity detection (no input for specified duration); when multiple end triggers are configured, system MUST terminate session when any trigger activates
- **FR-015**: System MUST support configuration of observation parameters per game (e.g., which event types to capture, screen capture frame rate with 15 FPS default, image format and quality)
- **FR-016**: System MUST write data to storage incrementally using buffering and asynchronous I/O to minimize performance impact
- **FR-017**: System MUST synchronize input event timestamps with screen capture frame timestamps to enable precise replay and analysis
- **FR-018**: System MUST generate unique session identifiers (UUID format) and collect session metadata including start/end times, participant ID (with optional anonymization via one-way hash to preserve cross-session linkability while protecting identity), game name, version, and platform
- **FR-019**: System MUST allow per-game configuration of ROI detection parameters including similarity match threshold (0.0-1.0 range), padding around detected region, periodic update interval for re-detection (default 5.0 seconds, configurable or can be disabled), and manual fallback coordinates
- **FR-019a**: System MUST retry ROI detection at configurable intervals (default 5 seconds) when automatic detection fails, pausing data collection until successful detection
- **FR-019b**: System MUST support manual override command to force immediate ROI re-detection regardless of configured update interval
- **FR-020**: System MUST support configurable trigger check intervals with the following specifications: start triggers using image-based detection default to 1.0 second check interval (configurable range: 0.5-5.0 seconds), end triggers for keyboard and timeout are checked every frame with minimal overhead, and ROI re-detection defaults to 5.0 second intervals (configurable or can be disabled)

### Key Entities *(include if feature involves data)*

- **Telemetry Event**: A single recorded player action including timestamp (millisecond precision), event type (keyboard/mouse), event-specific parameters (key code, mouse position, button ID), game identifier, and session identifier
- **Screen Capture Frame**: A captured image of the game screen or detected game region (ROI) at a specific timestamp, stored as JPEG or PNG with Unix timestamp in milliseconds embedded in filename (frame_<unix_timestamp_ms>.jpg) for efficient temporal correlation
- **Game Configuration**: Identification and observation settings for a specific game stored in structured format (YAML/JSON) containing: game profile name, ROI detection settings (method, reference image paths, match threshold, padding values, update interval), manual ROI fallback coordinates, session start triggers (type, parameters, check intervals) with OR logic, session end triggers (keyboard keys, timeout durations, inactivity thresholds) with OR logic, capture settings (frame rate, image quality), enabled event types, and output location
- **Collection Session**: A continuous period of telemetry recording tied to a single game execution instance, containing unique session ID (UUID), start/end timestamps, participant ID (optional/anonymized), game metadata (name/version/platform), and references to all input events and screen captures
- **Event Buffer**: Temporary in-memory storage for events and screen captures before they are written to persistent storage using asynchronous I/O, ensuring no data loss during high-frequency event periods
- **Region of Interest (ROI)**: The automatically detected rectangular area of the screen containing the game content, identified through template matching against reference images

## Dependencies and Assumptions

### Dependencies

- Target games must run on standard desktop operating systems (Windows, macOS, Linux)
- System requires read access to running process information on the host operating system
- Sufficient disk storage must be available for telemetry data (estimated 1-10MB per hour of gameplay depending on activity level)

### Assumptions

- Games expose standard input events through operating system APIs (keyboard hooks, mouse hooks)
- Researchers have basic file system navigation skills to configure the system and access collected data
- Game visual content can be reliably detected using template matching with reference screenshots
- Game window content is visible on screen (not completely obscured) during detection and recording
- Screen capture APIs are available on the target operating system with acceptable performance
- Reference screenshots provided by researchers clearly show distinctive game UI elements for reliable matching
- Standard data formats (JSON Lines, JSON, JPEG/PNG) are acceptable for downstream analysis tools
- Researchers can edit YAML or JSON configuration files with basic text editing tools
- Configuration files can reference external resources (images) via relative or absolute file paths
- Data collection occurs on the same machine where the game is running (not remote collection)
- Researchers will handle data storage management and archival independently (estimated 10-100MB per hour depending on screen capture settings; default 15 FPS at moderate quality typically requires 30-60MB per hour)
- Frame timestamps embedded in filenames enable O(1) temporal correlation between input events and screen captures without requiring sequential image loading or metadata parsing
- Analysis and visualization of collected data will be handled by separate tools in future phases
- Asynchronous I/O and buffering are sufficient for data durability (no distributed storage or replication required)
- Input events and screen captures from the same session can be synchronized using timestamps for accurate replay

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Researchers can configure and begin collecting data from a new game in under 5 minutes by editing a structured configuration file (YAML/JSON) without programming knowledge or system recompilation
- **SC-002**: System captures 99.9% of player input events during typical gameplay sessions (validated through synthetic test scenarios)
- **SC-003**: Event timestamps maintain accuracy within 10 milliseconds of actual occurrence time
- **SC-004**: System operates continuously for 4+ hour gameplay sessions without data loss or system crashes
- **SC-005**: Telemetry system overhead consumes less than 5% CPU and 100MB memory during active collection
- **SC-006**: Input event files use JSON Lines format and can be parsed line-by-line, metadata uses standard JSON format, and screen captures are stored as standard image files, all readable by common analysis tools without preprocessing
- **SC-006a**: Input event timestamps and screen capture frame timestamps maintain synchronization within 20 milliseconds on average, enabling accurate event-to-frame correlation with temporal interpolation support
- **SC-007**: System successfully manages telemetry for 3+ different games with distinct configurations without configuration conflicts or data mixing
- **SC-008**: 95% of recorded sessions contain complete data from game start to game termination without gaps or corruption
