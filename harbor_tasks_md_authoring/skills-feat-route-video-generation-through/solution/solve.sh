#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "1. **OpenClaw plugin mode** \u2014 If running inside OpenClaw and the `video_generate" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -61,16 +61,37 @@ You are a video producer. Not a form. Not a CLI wrapper. A producer who understa
 
 Detect in this order:
 
-1. **CLI mode (API-key override)** — If `HEYGEN_API_KEY` is set in the environment AND `heygen --version` exits 0, use CLI. API-key presence is an explicit user signal that they want direct API access; it short-circuits MCP detection. No question asked.
-2. **MCP mode** — No `HEYGEN_API_KEY` set AND HeyGen MCP tools are visible in the toolset (tools matching `mcp__heygen__*`). OAuth auth, uses existing plan credits.
-3. **CLI mode (fallback)** — MCP tools NOT available AND `heygen --version` exits 0. Auth via `heygen auth login` (persists to `~/.heygen/credentials`).
-4. **Neither** — tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."
+1. **OpenClaw plugin mode** — If running inside OpenClaw and the `video_generate` tool exposes a `heygen/video_agent_v3` model (i.e. the user has [`@heygen/openclaw-plugin-heygen`](https://github.com/heygen-com/openclaw-plugin-heygen) installed), prefer calling `video_generate({ model: "heygen/video_agent_v3", ... })` directly for video generation. The plugin handles auth (`HEYGEN_API_KEY`), session creation, polling, three-tier backoff, and error surfacing natively. Avatar discovery, voice listing, and avatar creation still go through MCP or CLI — only the final video-generate call routes through `video_generate`. Frame Check still runs before submission.
+2. **CLI mode (API-key override)** — If `HEYGEN_API_KEY` is set in the environment AND `heygen --version` exits 0, use CLI. API-key presence is an explicit user signal that they want direct API access; it short-circuits MCP detection. No question asked.
+3. **MCP mode** — No `HEYGEN_API_KEY` set AND HeyGen MCP tools are visible in the toolset (tools matching `mcp__heygen__*`). OAuth auth, uses existing plan credits.
+4. **CLI mode (fallback)** — MCP tools NOT available AND `heygen --version` exits 0. Auth via `heygen auth login` (persists to `~/.heygen/credentials`).
+5. **Neither** — tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."
 
 **Hard rules:**
-- **Never call `curl api.heygen.com/...`** — both modes route through their own surface.
+- **Never call `curl api.heygen.com/...`** — every mode routes through its own surface.
+- **OpenClaw plugin mode: only use `video_generate` for the generate step.** Never run `heygen ...` CLI for the generate call when the plugin is available. Avatar/voice discovery still uses MCP or CLI.
 - **MCP mode: only use `mcp__heygen__*` tools.** Never run `heygen ...` CLI commands. The MCP tool name IS the API.
 - **CLI mode: only use `heygen ...` commands.** Run `heygen <noun> <verb> --help` to discover arguments.
-- **Either mode: never cross over.** Operation blocks in the sub-skills show MCP and CLI side-by-side — read only the column for your detected mode, don't invoke anything from the other. If something isn't exposed in your current mode, tell the user; don't switch transports.
+- **Never cross over.** Operation blocks in the sub-skills show MCP and CLI side-by-side — read only the column for your detected mode, don't invoke anything from the other. If something isn't exposed in your current mode, tell the user; don't switch transports.
+
+### OpenClaw plugin-mode generate call
+
+```ts
+await video_generate({
+  model: "heygen/video_agent_v3",
+  prompt: scriptWithFrameCheckNotes,
+  aspectRatio: "16:9", // or "9:16"
+  providerOptions: {
+    avatar_id,
+    voice_id,
+    style_id,        // optional
+    callback_url,    // optional async webhook
+    callback_id,     // optional correlation id
+  },
+});
+```
+
+Plugin install (one-time, by the user): `openclaw plugins install clawhub:@heygen/openclaw-plugin-heygen`. Plugin docs: <https://github.com/heygen-com/openclaw-plugin-heygen>.
 
 ### MCP tool names (MCP mode only)
 
PATCH

echo "Gold patch applied."
