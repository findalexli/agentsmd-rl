#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-statusline

# Idempotency guard
if grep -qF "**Features**: 7-line statusline, native context % (v2.1.6+), prayer times, cost " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,11 +4,10 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## Project Status
 
-**Current**: v2.17.0 with session_mode component (Claude Code v2.1.6+)
-**Branch Strategy**: dev → nightly → main
-**Architecture**: Single Config.toml (227 settings), modular cache system (8 sub-modules), 91.5% code reduction from v1
-**Key Features**: 7-line statusline, native context window percentages (v2.1.6+), Islamic prayer times (GPS-accurate), cost tracking, MCP monitoring, cache isolation, health diagnostics (--health), metrics export (--metrics), JSON logging
-**Platform Support**: 100% compatibility on macOS, Ubuntu, Arch, Fedora, Alpine Linux with automatic platform detection
+**Current**: v2.17.0 | **Claude Code**: v2.1.6–v2.1.19 ✓ | **Branch**: dev → nightly → main
+**Architecture**: Single Config.toml (227 settings), modular cache (8 sub-modules), 91.5% code reduction
+**Features**: 7-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location
+**Platforms**: macOS, Ubuntu, Arch, Fedora, Alpine Linux
 
 ## Essential Commands
 
PATCH

echo "Gold patch applied."
