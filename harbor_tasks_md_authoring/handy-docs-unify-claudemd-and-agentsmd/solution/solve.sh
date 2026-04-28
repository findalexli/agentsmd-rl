#!/usr/bin/env bash
set -euo pipefail

cd /workspace/handy

# Idempotency guard
if grep -qF "The app enforces single instance behavior \u2014 launching when already running bring" "AGENTS.md" && grep -qF "Read @AGENTS.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,6 +1,6 @@
 # AGENTS.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+This file provides guidance to AI coding assistants working with code in this repository.
 
 ## Development Commands
 
@@ -29,51 +29,74 @@ bun run build      # Build frontend (TypeScript + Vite)
 bun run preview    # Preview built frontend
 ```
 
+**Linting and Formatting (run before committing):**
+
+```bash
+bun run lint              # ESLint for frontend
+bun run lint:fix          # ESLint with auto-fix
+bun run format            # Prettier + cargo fmt
+bun run format:check      # Check formatting without changes
+bun run format:frontend   # Prettier only
+bun run format:backend    # cargo fmt only
+```
+
 **Model Setup (Required for Development):**
 
 ```bash
-# Create models directory
 mkdir -p src-tauri/resources/models
-
-# Download required VAD model
 curl -o src-tauri/resources/models/silero_vad_v4.onnx https://blob.handy.computer/silero_vad_v4.onnx
 ```
 
-## Architecture Overview
+For detailed platform-specific build setup, see [BUILD.md](BUILD.md).
 
-Handy is a cross-platform desktop speech-to-text application built with Tauri (Rust backend + React/TypeScript frontend).
+## Architecture Overview
 
-### Core Components
+Handy is a cross-platform desktop speech-to-text application built with Tauri 2.x (Rust backend + React/TypeScript frontend).
 
-**Backend (Rust - src-tauri/src/):**
+### Backend Structure (src-tauri/src/)
 
-- `lib.rs` - Main application entry point with Tauri setup, tray menu, and managers
-- `managers/` - Core business logic managers:
+- `lib.rs` - Main entry point, Tauri setup, manager initialization
+- `managers/` - Core business logic:
   - `audio.rs` - Audio recording and device management
-  - `model.rs` - Whisper model downloading and management
+  - `model.rs` - Model downloading and management
   - `transcription.rs` - Speech-to-text processing pipeline
+  - `history.rs` - Transcription history storage
 - `audio_toolkit/` - Low-level audio processing:
   - `audio/` - Device enumeration, recording, resampling
-  - `vad/` - Voice Activity Detection using Silero VAD
+  - `vad/` - Voice Activity Detection (Silero VAD)
 - `commands/` - Tauri command handlers for frontend communication
+- `cli.rs` - CLI argument definitions (clap derive)
 - `shortcut.rs` - Global keyboard shortcut handling
 - `settings.rs` - Application settings management
-
-**Frontend (React/TypeScript - src/):**
-
-- `App.tsx` - Main application component with onboarding flow
-- `components/settings/` - Settings UI components
-- `components/model-selector/` - Model management interface
-- `hooks/` - React hooks for settings and model management
+- `overlay.rs` - Recording overlay window (platform-specific)
+- `signal_handle.rs` - `send_transcription_input()` reusable function
+- `utils.rs` - Platform detection helpers
+
+### Frontend Structure (src/)
+
+- `App.tsx` - Main component with onboarding flow
+- `components/` - React UI components:
+  - `settings/` - Settings UI
+  - `model-selector/` - Model management interface
+  - `onboarding/` - First-run experience
+  - `overlay/` - Recording overlay UI
+  - `update-checker/` - App update notifications
+  - `shared/`, `ui/`, `icons/`, `footer/` - Shared components
+- `hooks/useSettings.ts` - Settings state management hook
+- `stores/settingsStore.ts` - Zustand store for settings
+- `bindings.ts` - Auto-generated Tauri type bindings (via tauri-specta)
+- `overlay/` - Recording overlay window entry point
 - `lib/types.ts` - Shared TypeScript type definitions
 
 ### Key Architecture Patterns
 
-**Manager Pattern:** Core functionality is organized into managers (Audio, Model, Transcription) that are initialized at startup and managed by Tauri's state system.
+**Manager Pattern:** Core functionality organized into managers (Audio, Model, Transcription) initialized at startup and managed via Tauri state.
 
-**Command-Event Architecture:** Frontend communicates with backend via Tauri commands, backend sends updates via events.
+**Command-Event Architecture:** Frontend → Backend via Tauri commands; Backend → Frontend via events.
 
-**Pipeline Processing:** Audio → VAD → Whisper → Text output with configurable components at each stage.
+**Pipeline Processing:** Audio → VAD → Whisper/Parakeet → Text output → Clipboard/Paste
+
+**State Flow:** Zustand → Tauri Command → Rust State → Persistence (tauri-plugin-store)
 
 ### Technology Stack
 
@@ -86,12 +109,6 @@ Handy is a cross-platform desktop speech-to-text application built with Tauri (R
 - `rubato` - Audio resampling
 - `rodio` - Audio playback for feedback sounds
 
-**Platform-Specific Features:**
-
-- macOS: Metal acceleration for Whisper, accessibility permissions
-- Windows: Vulkan acceleration, code signing
-- Linux: OpenBLAS + Vulkan acceleration
-
 ### Application Flow
 
 1. **Initialization:** App starts minimized to tray, loads settings, initializes managers
@@ -111,4 +128,87 @@ Settings are stored using Tauri's store plugin with reactive updates:
 
 ### Single Instance Architecture
 
-The app enforces single instance behavior - launching when already running brings the settings window to front rather than creating a new process.
+The app enforces single instance behavior — launching when already running brings the settings window to front rather than creating a new process. Remote control flags (`--toggle-transcription`, etc.) work by launching a second instance that sends args to the running instance via `tauri_plugin_single_instance`, then exits.
+
+## Internationalization (i18n)
+
+All user-facing strings must use i18next translations. ESLint enforces this (no hardcoded strings in JSX).
+
+**Adding new text:**
+
+1. Add key to `src/i18n/locales/en/translation.json`
+2. Use in component: `const { t } = useTranslation(); t('key.path')`
+
+**File structure:**
+
+```
+src/i18n/
+├── index.ts           # i18n setup
+├── languages.ts       # Language metadata
+└── locales/
+    ├── en/translation.json  # English (source)
+    ├── de/, es/, fr/, ja/, ru/, zh/, ...
+    └── ...
+```
+
+For translation contribution guidelines, see [CONTRIBUTING_TRANSLATIONS.md](CONTRIBUTING_TRANSLATIONS.md).
+
+## Code Style
+
+**Rust:**
+
+- Run `cargo fmt` and `cargo clippy` before committing
+- Handle errors explicitly (avoid unwrap in production)
+- Use descriptive names, add doc comments for public APIs
+
+**TypeScript/React:**
+
+- Strict TypeScript, avoid `any` types
+- Functional components with hooks
+- Tailwind CSS for styling
+- Path aliases: `@/` → `./src/`
+
+## Commit Guidelines
+
+Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
+
+## CLI Parameters
+
+Handy supports command-line parameters on all platforms for integration with scripts, window managers, and autostart configurations.
+
+**Implementation:** `cli.rs` (definitions), `main.rs` (parsing), `lib.rs` (applying), `signal_handle.rs` (shared logic)
+
+| Flag                     | Description                                                    |
+| ------------------------ | -------------------------------------------------------------- |
+| `--toggle-transcription` | Toggle recording on/off on a running instance                  |
+| `--toggle-post-process`  | Toggle recording with post-processing on/off                   |
+| `--cancel`               | Cancel the current operation on a running instance             |
+| `--start-hidden`         | Launch without showing the main window (tray icon visible)     |
+| `--no-tray`              | Launch without system tray (closing window quits the app)      |
+| `--debug`                | Enable debug mode with verbose (Trace) logging                 |
+
+**Key design decisions:**
+
+- CLI flags are runtime-only overrides — they do NOT modify persisted settings
+- Remote control flags work via `tauri_plugin_single_instance`: second instance sends args, then exits
+- `send_transcription_input()` in `signal_handle.rs` is shared between signal handlers and CLI
+
+## Debug Mode
+
+Access debug features: `Cmd+Shift+D` (macOS) or `Ctrl+Shift+D` (Windows/Linux)
+
+## Platform Notes
+
+- **macOS**: Metal acceleration, accessibility permissions required for keyboard shortcuts
+- **Windows**: Vulkan acceleration, code signing
+- **Linux**: OpenBLAS + Vulkan, limited Wayland support, overlay uses GTK layer shell (disable with `HANDY_NO_GTK_LAYER_SHELL=1`)
+
+## Troubleshooting
+
+See the [Troubleshooting](README.md#troubleshooting) section in README.md.
+
+## Contributing & PR Guidelines
+
+Follow [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and [PR template](.github/PULL_REQUEST_TEMPLATE.md) when submitting pull requests. For translations, see [CONTRIBUTING_TRANSLATIONS.md](CONTRIBUTING_TRANSLATIONS.md).
+
+**Note:** Feature freeze is active — bug fixes are top priority. New features require community support via [Discussions](https://github.com/cjpais/Handy/discussions).
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,159 +1 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Development Commands
-
-**Prerequisites:** [Rust](https://rustup.rs/) (latest stable), [Bun](https://bun.sh/)
-
-```bash
-# Install dependencies
-bun install
-
-# Run in development mode
-bun run tauri dev
-# If cmake error on macOS:
-CMAKE_POLICY_VERSION_MINIMUM=3.5 bun run tauri dev
-
-# Build for production
-bun run tauri build
-
-# Linting and formatting (run before committing)
-bun run lint              # ESLint for frontend
-bun run lint:fix          # ESLint with auto-fix
-bun run format            # Prettier + cargo fmt
-bun run format:check      # Check formatting without changes
-```
-
-**Model Setup (Required for Development):**
-
-```bash
-mkdir -p src-tauri/resources/models
-curl -o src-tauri/resources/models/silero_vad_v4.onnx https://blob.handy.computer/silero_vad_v4.onnx
-```
-
-## Architecture Overview
-
-Handy is a cross-platform desktop speech-to-text app built with Tauri 2.x (Rust backend + React/TypeScript frontend).
-
-### Backend Structure (src-tauri/src/)
-
-- `lib.rs` - Main entry point, Tauri setup, manager initialization
-- `managers/` - Core business logic:
-  - `audio.rs` - Audio recording and device management
-  - `model.rs` - Model downloading and management
-  - `transcription.rs` - Speech-to-text processing pipeline
-  - `history.rs` - Transcription history storage
-- `audio_toolkit/` - Low-level audio processing:
-  - `audio/` - Device enumeration, recording, resampling
-  - `vad/` - Voice Activity Detection (Silero VAD)
-- `commands/` - Tauri command handlers for frontend communication
-- `shortcut.rs` - Global keyboard shortcut handling
-- `settings.rs` - Application settings management
-
-### Frontend Structure (src/)
-
-- `App.tsx` - Main component with onboarding flow
-- `components/settings/` - Settings UI (35+ files)
-- `components/model-selector/` - Model management interface
-- `components/onboarding/` - First-run experience
-- `hooks/useSettings.ts`, `useModels.ts` - State management hooks
-- `stores/settingsStore.ts` - Zustand store for settings
-- `bindings.ts` - Auto-generated Tauri type bindings (via tauri-specta)
-- `overlay/` - Recording overlay window code
-
-### Key Patterns
-
-**Manager Pattern:** Core functionality organized into managers (Audio, Model, Transcription) initialized at startup and managed via Tauri state.
-
-**Command-Event Architecture:** Frontend → Backend via Tauri commands; Backend → Frontend via events.
-
-**Pipeline Processing:** Audio → VAD → Whisper/Parakeet → Text output → Clipboard/Paste
-
-**State Flow:** Zustand → Tauri Command → Rust State → Persistence (tauri-plugin-store)
-
-## Internationalization (i18n)
-
-All user-facing strings must use i18next translations. ESLint enforces this (no hardcoded strings in JSX).
-
-**Adding new text:**
-
-1. Add key to `src/i18n/locales/en/translation.json`
-2. Use in component: `const { t } = useTranslation(); t('key.path')`
-
-**File structure:**
-
-```
-src/i18n/
-├── index.ts           # i18n setup
-├── languages.ts       # Language metadata
-└── locales/
-    ├── en/translation.json  # English (source)
-    ├── es/translation.json  # Spanish
-    ├── fr/translation.json  # French
-    └── vi/translation.json  # Vietnamese
-```
-
-## Code Style
-
-**Rust:**
-
-- Run `cargo fmt` and `cargo clippy` before committing
-- Handle errors explicitly (avoid unwrap in production)
-- Use descriptive names, add doc comments for public APIs
-
-**TypeScript/React:**
-
-- Strict TypeScript, avoid `any` types
-- Functional components with hooks
-- Tailwind CSS for styling
-- Path aliases: `@/` → `./src/`
-
-## Commit Guidelines
-
-Use conventional commits:
-
-- `feat:` new features
-- `fix:` bug fixes
-- `docs:` documentation
-- `refactor:` code refactoring
-- `chore:` maintenance
-
-## CLI Parameters
-
-Handy supports command-line parameters on all platforms for integration with scripts, window managers, and autostart configurations.
-
-**Implementation files:**
-
-- `src-tauri/src/cli.rs` - CLI argument definitions (clap derive)
-- `src-tauri/src/main.rs` - Argument parsing before Tauri launch
-- `src-tauri/src/lib.rs` - Applying CLI overrides (setup closure + single-instance callback)
-- `src-tauri/src/signal_handle.rs` - `send_transcription_input()` reusable function
-
-**Available flags:**
-
-| Flag                     | Description                                                                        |
-| ------------------------ | ---------------------------------------------------------------------------------- |
-| `--toggle-transcription` | Toggle recording on/off on a running instance (via `tauri_plugin_single_instance`) |
-| `--toggle-post-process`  | Toggle recording with post-processing on/off on a running instance                 |
-| `--cancel`               | Cancel the current operation on a running instance                                 |
-| `--start-hidden`         | Launch without showing the main window (tray icon still visible)                   |
-| `--no-tray`              | Launch without the system tray icon (closing window quits the app)                 |
-| `--debug`                | Enable debug mode with verbose (Trace) logging                                     |
-
-**Key design decisions:**
-
-- CLI flags are runtime-only overrides — they do NOT modify persisted settings
-- Remote control flags (`--toggle-transcription`, `--toggle-post-process`, `--cancel`) work by launching a second instance that sends its args to the running instance via `tauri_plugin_single_instance`, then exits
-- `send_transcription_input()` in `signal_handle.rs` is shared between signal handlers and CLI to avoid code duplication
-- `CliArgs` is stored in Tauri managed state (`.manage()`) so it's accessible in `on_window_event` and other handlers
-
-## Debug Mode
-
-Access debug features: `Cmd+Shift+D` (macOS) or `Ctrl+Shift+D` (Windows/Linux)
-
-## Platform Notes
-
-- **macOS**: Metal acceleration, accessibility permissions required
-- **Windows**: Vulkan acceleration, code signing
-- **Linux**: OpenBLAS + Vulkan, limited Wayland support, overlay disabled by default
+Read @AGENTS.md
PATCH

echo "Gold patch applied."
