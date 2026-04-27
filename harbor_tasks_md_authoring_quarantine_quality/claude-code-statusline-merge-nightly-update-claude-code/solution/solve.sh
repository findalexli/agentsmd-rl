#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-statusline

# Idempotency guard
if grep -qF "echo '{\"workspace\":{\"current_dir\":\"'$(pwd)'\"},\"model\":{\"display_name\":\"Claude Op" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,7 +4,7 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## Project Status
 
-**Current**: v2.17.0 | **Claude Code**: v2.1.6–v2.1.22 ✓ | **Branch**: dev → nightly → main
+**Current**: v2.17.0 | **Claude Code**: v2.1.6–v2.1.33 ✓ | **Branch**: dev → nightly → main
 **Architecture**: Single Config.toml (227 settings), modular cache (8 sub-modules), 91.5% code reduction
 **Features**: 7-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location
 **Platforms**: macOS, Ubuntu, Arch, Fedora, Alpine Linux
@@ -126,6 +126,34 @@ ENV_CONFIG_PRAYER_LOCATION_MODE=local_gps ./statusline.sh
 ENV_CONFIG_LOCATION_FORMAT=full ./statusline.sh
 ```
 
+## Claude Code JSON Input Format (stdin)
+
+The statusline reads JSON from stdin (`input=$(cat)`), exported as `STATUSLINE_INPUT_JSON` for all components. Only `workspace.current_dir` is required; all other fields are optional with graceful fallbacks.
+
+**Core Fields** (from Claude Code process):
+```json
+{
+  "workspace": { "current_dir": "/path/to/repo", "project_dir": "/path/to/repo" },
+  "model": { "display_name": "Claude Opus 4.5" },
+  "session_id": "uuid-string",
+  "transcript_path": "/path/to/transcript.jsonl",
+  "output_style": { "name": "default" },
+  "context_window": { "used_percentage": 12, "remaining_percentage": 88, "context_window_size": 200000 },
+  "cost": { "total_cost_usd": 0.45, "total_duration_ms": 60000, "total_api_duration_ms": 30000, "total_lines_added": 120, "total_lines_removed": 30 },
+  "current_usage": { "input_tokens": 10000, "cache_read_input_tokens": 5000, "cache_creation_input_tokens": 2000 },
+  "five_hour": { "utilization": 15.0, "resets_at": "2026-02-03T19:00:00Z" },
+  "seven_day": { "utilization": 19.0, "resets_at": "2026-02-08T08:00:00Z" },
+  "mcp": { "servers": [] }
+}
+```
+
+**Manual Test Command** (simulates Claude Code input):
+```bash
+echo '{"workspace":{"current_dir":"'$(pwd)'"},"model":{"display_name":"Claude Opus 4.5"},"context_window":{"used_percentage":12},"cost":{"total_cost_usd":0.45,"total_lines_added":120,"total_lines_removed":30},"current_usage":{"cache_read_input_tokens":5000,"input_tokens":10000},"session_id":"test","mcp":{"servers":[]}}' | /opt/homebrew/bin/bash ~/.claude/statusline/statusline.sh
+```
+
+**macOS Note**: Requires bash 4+ (`brew install bash`). Settings.json should use `/opt/homebrew/bin/bash` (Apple Silicon) or `/usr/local/bin/bash` (Intel) instead of `bash`.
+
 ## Testing & Debugging
 
 ```bash
PATCH

echo "Gold patch applied."
