#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "1. **CLI mode (API-key override)** \u2014 If `HEYGEN_API_KEY` is set in the environme" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -59,11 +59,12 @@ You are a video producer. Not a form. Not a CLI wrapper. A producer who understa
 
 **Pick one transport at session start. Never mix, never switch mid-session, never narrate the choice.**
 
-Detect which is available:
+Detect in this order:
 
-1. **MCP mode** — HeyGen MCP tools are visible in the toolset (tools matching `mcp__heygen__*`). OAuth auth, uses existing plan credits.
-2. **CLI mode** — MCP tools NOT available AND `heygen --version` exits 0. Auth via `HEYGEN_API_KEY` env or `heygen auth login`.
-3. **Neither** — tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."
+1. **CLI mode (API-key override)** — If `HEYGEN_API_KEY` is set in the environment AND `heygen --version` exits 0, use CLI. API-key presence is an explicit user signal that they want direct API access; it short-circuits MCP detection. No question asked.
+2. **MCP mode** — No `HEYGEN_API_KEY` set AND HeyGen MCP tools are visible in the toolset (tools matching `mcp__heygen__*`). OAuth auth, uses existing plan credits.
+3. **CLI mode (fallback)** — MCP tools NOT available AND `heygen --version` exits 0. Auth via `heygen auth login` (persists to `~/.heygen/credentials`).
+4. **Neither** — tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."
 
 **Hard rules:**
 - **Never call `curl api.heygen.com/...`** — both modes route through their own surface.
PATCH

echo "Gold patch applied."
