#!/usr/bin/env bash
set -euo pipefail

cd /workspace/voicemode

# Idempotency guard
if grep -qF "- **[skills/voicemode/SKILL.md](skills/voicemode/SKILL.md)** - Voice interaction" "CLAUDE.md" && grep -qF "agents.md" "agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,6 +2,10 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
+## Voice Interaction
+
+Load the voicemode skill for voice conversation support: `/voicemode:voicemode`
+
 ## Project Overview
 
 VoiceMode is a Python package that provides voice interaction capabilities for AI assistants through the Model Context Protocol (MCP). It enables natural voice conversations with Claude Code and other AI coding assistants by integrating speech-to-text (STT) and text-to-speech (TTS) services.
@@ -24,25 +28,6 @@ uv run pytest tests/test_voice_mode.py -v
 make clean
 ```
 
-### Configuration Management
-```bash
-# Edit configuration file in default editor
-voicemode config edit
-
-# Or specify a different editor
-voicemode config edit --editor vim
-voicemode config edit --editor "code --wait"
-
-# List available configuration keys
-voicemode config list
-
-# Get a specific configuration value
-voicemode config get VOICEMODE_TTS_VOICE
-
-# Set a configuration value
-voicemode config set VOICEMODE_TTS_VOICE nova
-```
-
 ### Building & Publishing
 ```bash
 # Build Python package
@@ -135,40 +120,22 @@ Services can be installed and managed through MCP tools, with automatic service
 - Event logging and conversation logging are available for debugging
 - WebRTC VAD is used for silence detection when available
 
-## Testing Approach
+## Testing
 
-- Unit tests are in the `tests/` directory
-- Manual tests requiring user interaction are in `tests/manual/`
-- Use `pytest` for running tests, with fixtures for mocking external services
-- Integration tests verify service discovery and provider selection
-- The project includes comprehensive test coverage for configuration, providers, and tools
+- Unit tests: `tests/` - run with `make test`
+- Manual tests: `tests/manual/` - require user interaction
 
 ## Logging
 
-VoiceMode maintains comprehensive logs in the `~/.voicemode/` directory:
-
-```
-~/.voicemode/
-├── logs/
-│   ├── conversations/     # JSONL files with daily conversation exchanges
-│   │   └── exchanges_YYYY-MM-DD.jsonl
-│   ├── events/           # JSONL files with detailed event logs
-│   │   └── voicemode_events_YYYY-MM-DD.jsonl
-│   └── debug/            # Debug logs when debug mode is enabled
-├── audio/                # Saved audio recordings organized by date
-│   └── YYYY/MM/         # TTS and STT audio files (.wav format)
-├── config/               # User configuration files
-│   ├── config.yaml       # Main configuration
-│   └── pronunciation.yaml # Custom pronunciation rules
-└── services/             # Installed voice services (Whisper, Kokoro, LiveKit)
-    ├── whisper/         # Whisper.cpp installation and models
-    ├── kokoro/          # Kokoro TTS service
-    └── livekit/         # LiveKit server and agents
-```
+Logs are stored in `~/.voicemode/`:
+- `logs/conversations/` - Voice exchange history (JSONL)
+- `logs/events/` - Operational events and errors
+- `audio/` - Saved TTS/STT audio files
+- `voicemode.env` - User configuration
 
-### Log Types
+## See Also
 
-- **Conversation Logs** (`logs/conversations/`): Records of voice exchanges including timestamps, text, and metadata
-- **Event Logs** (`logs/events/`): Detailed operational events including TTS/STT operations, errors, and provider selection
-- **Audio Recordings** (`audio/`): Saved TTS outputs and STT inputs for debugging and review
-- **Debug Logs** (`logs/debug/`): Verbose debugging information when running with `--debug` flag
\ No newline at end of file
+- **[skills/voicemode/SKILL.md](skills/voicemode/SKILL.md)** - Voice interaction usage and MCP tools
+- **[docs/tutorials/getting-started.md](docs/tutorials/getting-started.md)** - Installation guide
+- **[docs/guides/configuration.md](docs/guides/configuration.md)** - Configuration reference
+- **[docs/concepts/architecture.md](docs/concepts/architecture.md)** - Detailed architecture
\ No newline at end of file
diff --git a/agents.md b/agents.md
@@ -0,0 +1 @@
+CLAUDE.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
