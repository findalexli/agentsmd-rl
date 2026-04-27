#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "- `area: distribution` \u2014 Nix flake, cargo-dist, npm packaging, install methods" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -150,6 +150,19 @@ When adding a new helper or CLI command:
 5. **Resource names** (project IDs, space names, topic names) → Use `validate_resource_name()`
 6. **Write tests** for both the happy path AND the rejection path (e.g., pass `../../.ssh` and assert `Err`)
 
+## PR Labels
+
+Use these labels to categorize pull requests and issues:
+
+- `area: discovery` — Discovery document fetching, caching, parsing
+- `area: http` — Request execution, URL building, response handling
+- `area: docs` — README, contributing guides, documentation
+- `area: tui` — Setup wizard, picker, input fields
+- `area: distribution` — Nix flake, cargo-dist, npm packaging, install methods
+- `area: mcp` — Model Context Protocol server/tools
+- `area: auth` — OAuth, credentials, multi-account, ADC
+- `area: skills` — AI skill generation and management
+
 ## Environment Variables
 
 - `GOOGLE_WORKSPACE_CLI_TOKEN` — Pre-obtained OAuth2 access token (highest priority; bypasses all credential file loading)
PATCH

echo "Gold patch applied."
