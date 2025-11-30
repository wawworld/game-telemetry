# Input Capture Library Research

## Decision: rdev (Rust) with Python bindings via PyO3

## Rationale

After evaluating multiple input capture libraries across Python, Rust, and C++, **rdev** emerges as the optimal choice for cross-platform input monitoring with minimal overhead. Here's why:

**Performance & Architecture**: rdev uses native OS APIs directly (X11 on Linux, Cocoa on macOS, Win32 on Windows) without intermediate layers, providing sub-millisecond latency and negligible CPU overhead (<0.1% for passive listening). The library implements a blocking callback pattern that processes events immediately as they arrive from the OS, avoiding polling overhead.

**Cross-Platform Completeness**: Unlike alternatives with platform-specific gaps, rdev provides full keyboard and mouse event capture on all three major platforms. It captures key codes, timestamps, mouse coordinates, buttons, and scroll deltas consistently. The `Event` struct includes `SystemTime` timestamps with nanosecond precision, essential for accurate telemetry. The library handles platform quirks transparently (e.g., dead keys on Linux, accessibility API on macOS).

**Non-Blocking Operation**: While the `listen()` function blocks the calling thread, rdev's callback-based design naturally supports spawning the listener on a dedicated thread, making the system non-blocking for the main application. Events are delivered asynchronously through callbacks with zero queuing delay. For more advanced use cases, the `unstable_grab` feature enables event interception before delivery to applications.

**Integration Strategy**: For a Python-based telemetry system, wrap rdev in a thin PyO3 layer to expose Rust performance to Python consumers. This provides the best of both worlds: Rust's efficiency for event capture with Python's flexibility for data processing and transmission. Alternatively, use rdev directly in a Rust service that communicates with Python via IPC/gRPC.

## Alternatives Considered

### pynput (Python)
- **Platform Support**: Full support for Windows/macOS/Linux (X11), with optional uinput backend for Linux
- **Performance**: Pure Python with platform-specific backends (pyobjc on macOS, ctypes on Windows, Xlib on Linux). Adds ~10-50ms latency due to GIL and cross-language overhead. CPU usage typically 0.3-0.5% for passive listening
- **Permissions**: 
  - macOS: Requires Accessibility API permissions (same as rdev)
  - Linux: Requires X11 session; uinput backend requires root
  - Windows: No special permissions
- **API**: Thread-based listener with blocking or non-blocking modes. Clean Pythonic API with `Listener` classes and callbacks
- **Pros**: 
  - Native Python library, no compilation needed
  - Well-documented with extensive examples
  - Active maintenance (2k stars, regular updates)
  - Thread-based architecture fits Python concurrency model
  - Includes keyboard state tracking and layout awareness
- **Cons**: 
  - Higher overhead than native solutions (10-50ms latency)
  - GIL limitations for high-frequency events
  - Timestamp precision depends on Python's `time.time()` (microseconds vs nanoseconds)
  - Wayland support requires root via uinput backend

### keyboard + mouse (Python)
- **Platform Support**: Windows and Linux (requires sudo), experimental macOS support
- **Performance**: Similar to pynput (~0.3-0.5% CPU). Uses raw device files (`/dev/input/input*`) on Linux
- **Permissions**:
  - Linux: **Requires root** to read from `/dev/input/input*`
  - macOS: Experimental, requires Accessibility API
  - Windows: No special permissions
- **API**: Global hooks with various helper functions (`keyboard.on_press()`, `mouse.on_move()`)
- **Pros**:
  - Simple API with many convenience functions
  - Popular (4k+ stars for keyboard)
  - Events captured in separate thread automatically
- **Cons**:
  - **Currently unmaintained** (keyboard repo explicitly states this)
  - Linux requires root privileges (deal-breaker for user applications)
  - macOS support is experimental and unreliable
  - No key suppression on Linux
  - Separate packages that must be coordinated
  - Limited timestamp precision

### evdev (Linux only)
- **Platform Support**: Linux only (X11 and Wayland)
- **Performance**: Excellent (<0.1% CPU), direct access to kernel input subsystem
- **Permissions**: Requires membership in `input` or `plugdev` group (not root, but elevated)
- **API**: Low-level Python bindings to libevdev. Async-friendly with `asyncio` support
- **Pros**:
  - Works on both X11 and Wayland
  - Very low overhead, direct kernel access
  - Supports asyncio
  - Precise timestamps from kernel
- **Cons**:
  - Linux only, requires separate solution for Windows/macOS
  - Requires group membership (still elevated privileges)
  - Lower-level API, more complex to use
  - Need to handle multiple input devices manually

### pyautogui (Python)
- **Platform Support**: Windows, macOS, Linux (X11)
- **Performance**: Not designed for monitoring; primarily for automation. High overhead when polling
- **Permissions**: Same as pynput (platform-dependent)
- **API**: Primarily for simulation, not capture. Can query state but requires polling
- **Pros**:
  - Well-known library (12k+ stars)
  - Cross-platform
  - Good for simulation/automation
- **Cons**:
  - **Not designed for event capture** - requires polling instead of callbacks
  - High CPU usage for polling-based monitoring (5-15%)
  - No timestamp information on captured events
  - Missing key release events
  - Screenshot-focused, input capture is secondary
  - Not suitable for this use case

### device_query (Rust)
- **Platform Support**: Windows, macOS, Linux (X11)
- **Performance**: Lightweight polling-based approach. ~0.5-1% CPU with 10ms poll interval
- **Permissions**:
  - macOS: Requires Accessibility permissions
  - Linux: Requires X11 development libraries
  - Windows: No special permissions
- **API**: Polling-based state queries (`get_keys()`, `get_mouse()`). Recently added callback support via `DeviceEventsHandler`
- **Pros**:
  - Simple API, easy to use
  - No blocking calls in polling mode
  - Cross-platform
  - MIT licensed
  - Callback support added recently
- **Cons**:
  - Polling-based by default (callbacks are new)
  - Higher CPU than event-driven approaches
  - Less precise timestamps (depends on poll rate)
  - Missing some events between polls
  - Smaller community (197 stars)
  - Less actively maintained than rdev

### inputbot (Rust)
- **Platform Support**: Windows and Linux only (X11 only, not Wayland)
- **Performance**: Efficient event-driven approach, <0.2% CPU
- **Permissions**:
  - Linux: **Requires root (sudo)** via libinput
  - Windows: No special permissions
- **API**: Callback-based hotkey binding system (`bind()`, `handle_input_events()`)
- **Pros**:
  - Clean API for hotkey binding
  - Event-driven architecture
  - Active development (447 stars)
- **Cons**:
  - **No macOS support** (deal-breaker)
  - **Requires root on Linux** via libinput
  - Primarily designed for hotkeys/automation, not passive monitoring
  - Linux doesn't support Wayland natively
  - More complex to set up (libinput dependencies)

### Platform-Specific C++ APIs
- **Windows Hooks** (SetWindowsHookEx with WH_KEYBOARD_LL/WH_MOUSE_LL)
  - **Performance**: Excellent (<0.1% CPU), lowest possible latency
  - **Permissions**: No special permissions required
  - **Pros**: Direct OS integration, maximum performance, extensive documentation
  - **Cons**: Windows only, requires C++ expertise, complex to build cross-platform
  
- **X11/XRecord** (Linux)
  - **Performance**: Very good (<0.2% CPU)
  - **Permissions**: X11 session required, no root needed
  - **Pros**: Works on X11, standard approach
  - **Cons**: Doesn't work on Wayland, requires X11 dev libraries, complex API
  
- **macOS CGEvent** (Quartz Event Services)
  - **Performance**: Excellent (<0.1% CPU)
  - **Permissions**: Accessibility API access required
  - **Pros**: Official Apple API, maximum performance
  - **Cons**: macOS only, requires Objective-C/Swift knowledge, complex
  
- **Overall Assessment**:
  - **Pros**: Maximum performance, complete control, lowest level access
  - **Cons**: 
    - Requires maintaining three separate codebases
    - Complex build system for cross-compilation
    - High development/maintenance cost
    - Need C++ expertise across all platforms
    - Platform-specific quirks and bugs
    - Not justified unless sub-0.1% CPU is critical requirement

## Implementation Recommendation

**Phase 1 - Prototype (Python)**: Start with **pynput** for rapid prototyping. Despite higher overhead, it provides adequate performance (<1% CPU) for initial development and has the cleanest Python API. This allows focus on telemetry logic and data pipeline without dealing with FFI complexity.

**Phase 2 - Production (Rust)**: Migrate to **rdev** for production deployment. Two approaches:
1. **Pure Rust service**: Build input capture as a standalone Rust service that sends telemetry data via gRPC/protobuf to Python analytics backend
2. **Python extension**: Wrap rdev in PyO3 to create a native Python module with Rust performance

**Key Advantages of This Approach**:
- Rapid iteration during development (pynput)
- Production-grade performance in deployment (rdev)
- Clear migration path with minimal API changes
- Future-proof architecture that can scale to high-frequency capture
- No root/elevated permissions required (except Linux `input` group for rdev's `grab` feature)
- Full cross-platform support maintained throughout

**Permission Requirements Summary**:
- **Windows**: No special permissions for any solution
- **macOS**: Accessibility API permissions (one-time user approval, applies to all solutions)
- **Linux**: 
  - Basic listening: No special permissions (X11 required)
  - Event grabbing/blocking: Add user to `input` group (no root needed)
  - Wayland: Use evdev or rdev with `input` group membership

## Performance Comparison Table

| Library | CPU Overhead | Latency | Timestamp Precision | Non-Blocking |
|---------|--------------|---------|---------------------|--------------|
| rdev (Rust) | <0.1% | <1ms | Nanosecond | Yes (thread) |
| pynput (Python) | 0.3-0.5% | 10-50ms | Microsecond | Yes (thread) |
| keyboard+mouse (Python) | 0.3-0.5% | 10-50ms | Microsecond | Yes (thread) |
| device_query (Rust) | 0.5-1%* | 10ms* | Depends on poll | Yes |
| inputbot (Rust) | <0.2% | 1-2ms | Nanosecond | Yes (thread) |
| evdev (Python) | <0.1% | 1-2ms | Nanosecond | Yes (async) |
| pyautogui (Python) | 5-15%* | 100ms+ | None | No |

*Polling-based, overhead depends on poll rate

## Conclusion

**rdev** provides the optimal balance of performance, cross-platform support, and API ergonomics for a game telemetry system. Its direct OS integration, nanosecond timestamps, and minimal overhead make it production-ready for capturing high-frequency input events without impacting game performance. The suggested two-phase approach (pynput → rdev) balances development velocity with production performance requirements.
