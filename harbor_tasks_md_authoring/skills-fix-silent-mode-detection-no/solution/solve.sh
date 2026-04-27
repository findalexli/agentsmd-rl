#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cl" "SKILL.md" && grep -qF "**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cl" "heygen-avatar/SKILL.md" && grep -qF "**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cl" "heygen-video/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -57,11 +57,13 @@ You are a video producer. Not a form. Not a CLI wrapper. A producer who understa
 
 ## API Mode Detection
 
-Two modes, in order of preference:
+Two modes, in order of preference. **Mode selection is silent — detect once at the start of the session, pick a mode, and move on.** Never narrate transport choice ("CLI is broken", "switching to MCP") — the user doesn't care how calls are made.
 
 **MCP (preferred):** If HeyGen MCP tools are available (tools matching `mcp__heygen__*`), use them. MCP authenticates via OAuth — no API key needed — and runs against the user's existing HeyGen plan credits. Endpoint: `https://mcp.heygen.com/mcp/v1/`.
 
-**CLI fallback:** If MCP tools are not available, use the [HeyGen CLI](https://github.com/heygen-com/heygen-cli) (`heygen` binary). Install: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash`. Auth: set `HEYGEN_API_KEY` in the env OR run `heygen auth login` (persists to `~/.heygen/credentials`). Verify with `heygen auth status`. If neither auth source is set, tell the user: "No HeyGen auth found. Run `heygen auth login` or set `export HEYGEN_API_KEY=<your-key>`."
+**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: set `HEYGEN_API_KEY` in the env OR run `heygen auth login` (persists to `~/.heygen/credentials`). If the CLI binary is missing, errors on `--version`, or auth is not set, silently skip it — do not retry MCP.
+
+**Neither available:** Only if both MCP and a working CLI are missing, tell the user once — concisely — how to connect: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."
 
 CLI output is JSON on stdout, structured error envelopes on stderr, and stable exit codes: `0` ok · `1` API/network · `2` usage · `3` auth · `4` timeout under `--wait`. Pipe to `jq` to extract fields.
 
diff --git a/heygen-avatar/SKILL.md b/heygen-avatar/SKILL.md
@@ -55,9 +55,13 @@ Wait for their answer before proceeding.
 
 ## API Mode Detection
 
+**Mode selection is silent.** Detect once at the start of the session, pick a mode, move on. Never narrate transport choice ("CLI is broken", "switching to MCP") — the user doesn't care how calls are made.
+
 **MCP (preferred):** If HeyGen MCP tools are available (tools matching `mcp__heygen__*`), use them. MCP authenticates via OAuth — no API key needed — and runs against the user's existing HeyGen plan credits.
 
-**CLI fallback:** If MCP tools are not available, use the [HeyGen CLI](https://github.com/heygen-com/heygen-cli) (`heygen` binary). Auth: set `HEYGEN_API_KEY` in the env OR run `heygen auth login` (persists to `~/.heygen/credentials`). Verify with `heygen auth status`. If neither auth source is set, tell the user to run `heygen auth login` or `export HEYGEN_API_KEY=<key>`.
+**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: `HEYGEN_API_KEY` env OR `heygen auth login` (persists to `~/.heygen/credentials`). If the CLI is missing, errors on `--version`, or auth is not set, silently skip it — do not retry MCP.
+
+**Neither available:** Only if MCP is unavailable AND the CLI doesn't work, tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."
 
 **API:** v3 only. Never call v1 or v2 endpoints.
 
diff --git a/heygen-video/SKILL.md b/heygen-video/SKILL.md
@@ -45,11 +45,13 @@ You are a video producer. Not a form. Not a CLI wrapper. A producer who understa
 
 ## API Mode Detection
 
-Two modes, in order of preference:
+Two modes, in order of preference. **Mode selection is silent.** Detect once at the start of the session, pick a mode, move on. Never narrate transport choice ("CLI is broken", "switching to MCP") — the user doesn't care how calls are made.
 
 **MCP (preferred):** If HeyGen MCP tools are available (tools matching `mcp__heygen__*`), use them. MCP authenticates via OAuth — no API key needed — and runs against the user's existing HeyGen plan credits.
 
-**CLI fallback:** If MCP tools are not available, use the [HeyGen CLI](https://github.com/heygen-com/heygen-cli) (`heygen` binary). Auth: set `HEYGEN_API_KEY` in the env OR run `heygen auth login` (persists to `~/.heygen/credentials`). Verify with `heygen auth status`. If neither auth source is set, tell the user to run `heygen auth login` or `export HEYGEN_API_KEY=<key>`.
+**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: `HEYGEN_API_KEY` env OR `heygen auth login` (persists to `~/.heygen/credentials`). If the CLI is missing, errors on `--version`, or auth is not set, silently skip it — do not retry MCP.
+
+**Neither available:** Only if MCP is unavailable AND the CLI doesn't work, tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."
 
 CLI output: JSON on stdout, structured error envelope on stderr, stable exit codes (0 ok · 1 API · 2 usage · 3 auth · 4 timeout). Pipe to `jq` to extract fields. Add `--wait` on creation commands to block on completion instead of hand-rolling a poll loop.
 
PATCH

echo "Gold patch applied."
