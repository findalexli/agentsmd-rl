#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-statusline

# Idempotency guard
if grep -qF "**Data Flow**: JSON input \u2192 Config loading \u2192 Theme application \u2192 Atomic componen" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,16 +4,16 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## Project Status
 
-**Current**: v2.18.0 | **Claude Code**: v2.1.6–v2.1.42 ✓ | **Branch**: feat/fix/chore → nightly → main
+**Current**: v2.19.0 | **Claude Code**: v2.1.6–v2.1.42 ✓ | **Branch**: feat/fix/chore → nightly → main
 **Architecture**: Single Config.toml (227 settings), modular cache (8 sub-modules), 91.5% code reduction
-**Features**: 7-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location
+**Features**: 9-line statusline, native context % (v2.1.6+), prayer times, cost tracking, MCP, GPS location, wellness, CLI analytics
 **Platforms**: macOS, Ubuntu, Arch, Fedora, Alpine Linux
 
 ## Essential Commands
 
 ```bash
 # Testing & Development
-npm test                              # Run all 254 tests across 17 files
+npm test                              # Run all 838 tests across 48 files
 npm run lint:all                     # Lint everything
 ./statusline.sh --modules             # Show component status
 STATUSLINE_DEBUG=true ./statusline.sh # Debug mode
@@ -37,17 +37,19 @@ bats tests/unit/test_platform_compatibility.bats
 
 ## Architecture
 
-**Core Modules** (11): core → security → config → themes → cache → git → mcp → cost → prayer → components → display
+**Core Modules** (14): core → security → config → themes → cache → git → mcp → cost → prayer → wellness → focus → components → display
 
-**Atomic Components** (21):
+**Atomic Components** (22):
 - **Repository & Git** (4): repo_info, commits, submodules, version_info
 - **Model & Session** (4): model_info, cost_repo, cost_live, reset_timer
 - **Cost Analytics** (3): cost_monthly, cost_weekly, cost_daily
 - **Block Metrics** (4): burn_rate, token_usage, cache_efficiency, block_projection
 - **System** (2): mcp_status, time_display
+- **Wellness** (1): wellness (idle detection, focus mode, break reminders)
 - **Spiritual** (2): prayer_times, location_display
+- **CLI Analytics** (10 commands): --commits, --mcp-costs, --recommendations, --trends, --limits, --watch, --csv, --focus
 
-**Data Flow**: JSON input → Config loading → Theme application → Atomic component data collection → 1-9 line dynamic output (default: 7-line with GPS-accurate location display)
+**Data Flow**: JSON input → Config loading → Theme application → Atomic component data collection → 1-9 line dynamic output (default: 9-line with wellness + GPS location)
 
 **Key Functions**:
 - `load_module()` - Module loading with dependency checking
@@ -68,9 +70,9 @@ git push origin feat/my-feature           # Push feature
 git checkout nightly && git merge feat/my-feature --no-ff  # Merge to nightly
 
 # Testing
-bats tests/unit/test_*.bats           # Unit tests (9 files)
-bats tests/integration/test_*.bats    # Integration tests (6 files)
-bats tests/benchmarks/test_*.bats     # Performance tests (2 files)
+bats tests/unit/test_*.bats           # Unit tests (37 files)
+bats tests/integration/test_*.bats    # Integration tests (7 files)
+bats tests/benchmarks/test_*.bats     # Performance tests (4 files)
 
 # Pre-commit hooks (optional but recommended)
 pip install pre-commit && pre-commit install
PATCH

echo "Gold patch applied."
