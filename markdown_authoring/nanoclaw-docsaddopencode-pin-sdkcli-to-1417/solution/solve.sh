#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "- `ANTHROPIC_BASE_URL` \u2014 **required for non-`anthropic` providers.** The opencod" ".claude/skills/add-opencode/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-opencode/SKILL.md b/.claude/skills/add-opencode/SKILL.md
@@ -60,10 +60,10 @@ import './opencode.js';
 
 ### 4. Add the agent-runner dependency
 
-Pinned. Bump deliberately, not with `bun update`.
+Pinned. Bump deliberately, not with `bun update`. Use `1.4.17` — must match the `opencode-ai` CLI version pinned in step 5. The 1.14.x SDK has a completely different API and is **incompatible** with the current provider code.
 
 ```bash
-cd container/agent-runner && bun add @opencode-ai/sdk@1.4.3 && cd -
+cd container/agent-runner && bun add @opencode-ai/sdk@1.4.17 && cd -
 ```
 
 ### 5. Add `opencode-ai` to the container Dockerfile
@@ -73,9 +73,11 @@ Two edits to `container/Dockerfile`, both idempotent (skip if already present):
 **(a)** In the "Pin CLI versions" ARG block (around line 18), add after `ARG VERCEL_VERSION=latest`:
 
 ```dockerfile
-ARG OPENCODE_VERSION=latest
+ARG OPENCODE_VERSION=1.4.17
 ```
 
+> **Do not use `latest`** — the CLI and SDK must be the same version. `latest` silently upgrades the CLI to 1.14.x which has a breaking session API change (UUID session IDs → `ses_` prefix) incompatible with SDK 1.4.x.
+
 **(b)** In the `pnpm install -g` block (around line 80), append `"opencode-ai@${OPENCODE_VERSION}"` to the list:
 
 ```dockerfile
@@ -94,6 +96,25 @@ pnpm exec tsc -p container/agent-runner/tsconfig.json --noEmit   # container typ
 ./container/build.sh                                   # agent image
 ```
 
+> **Build cache gotcha:** The container buildkit caches COPY steps aggressively. If provider files were already present in the build context before, the new files may not be picked up. If you see "Unknown provider: opencode" after the build, prune the builder and rebuild:
+> ```bash
+> docker builder prune -f && ./container/build.sh
+> ```
+
+### 7. Propagate to existing per-group overlays
+
+Each agent group has a live source overlay at `data/v2-sessions/<group-id>/agent-runner-src/providers/` that **overrides the image at runtime**. This overlay is created when the group is first wired and never auto-updated by image rebuilds. Any group that already existed before this skill ran needs the new files copied in manually.
+
+```bash
+for overlay in data/v2-sessions/*/agent-runner-src/providers/; do
+  [ -d "$overlay" ] || continue
+  cp container/agent-runner/src/providers/opencode.ts "$overlay"
+  cp container/agent-runner/src/providers/mcp-to-opencode.ts "$overlay"
+  cp container/agent-runner/src/providers/index.ts "$overlay"
+  echo "Updated: $overlay"
+done
+```
+
 ## Configuration
 
 ### Host `.env` (typical)
@@ -102,35 +123,62 @@ Set model/provider strings in the form OpenCode expects (often `provider/model-i
 
 These variables are read **on the host** and passed into the container only when the effective provider is `opencode`. They do not switch the provider by themselves; the DB still needs `agent_provider` set (below).
 
-- `OPENCODE_PROVIDER` — OpenCode provider id, e.g. `openrouter`, `anthropic` (if unset, the runner defaults to `anthropic`).
-- `OPENCODE_MODEL` — full model id, e.g. `openrouter/anthropic/claude-sonnet-4`.
-- `OPENCODE_SMALL_MODEL` — optional second model for "small" tasks.
+- `OPENCODE_PROVIDER` — OpenCode provider id, e.g. `openrouter`, `anthropic`, `deepseek`.
+- `OPENCODE_MODEL` — full model id in `provider/model` form, e.g. `deepseek/deepseek-chat`.
+- `OPENCODE_SMALL_MODEL` — optional second model for lighter tasks; defaults to `OPENCODE_MODEL` if unset.
+- `ANTHROPIC_BASE_URL` — **required for non-`anthropic` providers.** The opencode container provider passes this as the `baseURL` for the upstream provider config so requests route through OneCLI's credential proxy or directly to the provider's API. Set it to the provider's API base URL (e.g. `https://api.deepseek.com/v1`, `https://openrouter.ai/api/v1`).
+
+Credentials: register provider API keys in OneCLI with the matching `--host-pattern` (e.g. `api.deepseek.com`, `openrouter.ai`). OneCLI injects them via `HTTPS_PROXY` in the container — the key never lives in `.env` or the container environment.
 
-Credentials: OneCLI / credential proxy patterns are unchanged. For non-`anthropic` OpenCode providers, the runner registers a placeholder API key and **`ANTHROPIC_BASE_URL`** (the credential proxy) as `baseURL` so the real key never lives in the container.
+After adding a secret, **grant the agent access** — agents in `selective` mode only receive secrets they've been explicitly assigned:
+
+```bash
+# Find the agent id and secret id, then:
+onecli agents set-secrets --id <agent-id> --secret-ids <existing-ids>,<new-secret-id>
+```
+
+Always include existing secret IDs in the list — `set-secrets` replaces, not appends.
+
+#### Example: DeepSeek
+
+```env
+OPENCODE_PROVIDER=deepseek
+OPENCODE_MODEL=deepseek/deepseek-chat
+OPENCODE_SMALL_MODEL=deepseek/deepseek-chat
+ANTHROPIC_BASE_URL=https://api.deepseek.com/v1
+```
+
+Register the key:
+```bash
+onecli secrets create --name "DeepSeek" --type generic \
+  --value YOUR_KEY --host-pattern "api.deepseek.com" \
+  --header-name "Authorization" --value-format "Bearer {value}"
+```
 
 #### Example: OpenRouter
 
 ```env
-# OpenCode — host passes these into the container when agent_provider is opencode
 OPENCODE_PROVIDER=openrouter
 OPENCODE_MODEL=openrouter/anthropic/claude-sonnet-4
 OPENCODE_SMALL_MODEL=openrouter/anthropic/claude-haiku-4.5
+ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
+```
+
+Register the key:
+```bash
+onecli secrets create --name "OpenRouter" --type generic \
+  --value YOUR_KEY --host-pattern "openrouter.ai" \
+  --header-name "Authorization" --value-format "Bearer {value}"
 ```
 
-#### Example: Anthropic via existing proxy env
+#### Example: Anthropic (no ANTHROPIC_BASE_URL needed)
 
-When `OPENCODE_PROVIDER` is `anthropic`, OpenCode uses normal Anthropic env inside the container (proxy + placeholder key pattern unchanged).
+When `OPENCODE_PROVIDER` is `anthropic`, OpenCode uses normal Anthropic env inside the container — the proxy + placeholder key pattern is unchanged and `ANTHROPIC_BASE_URL` is not required.
 
 ```env
 OPENCODE_PROVIDER=anthropic
 OPENCODE_MODEL=anthropic/claude-sonnet-4-20250514
-```
-
-#### Example: only a main model
-
-```env
-OPENCODE_PROVIDER=openrouter
-OPENCODE_MODEL=openrouter/google/gemini-2.5-pro-preview
+OPENCODE_SMALL_MODEL=anthropic/claude-haiku-4-5-20251001
 ```
 
 #### OpenCode Zen (`x-api-key`, not Bearer)
@@ -142,13 +190,9 @@ Zen's HTTP API (e.g. `POST …/zen/v1/messages`) expects the key in the **`x-api
 **Host `.env` (typical Zen shape):**
 
 ```env
-# NanoClaw still resolves AGENT_PROVIDER from agent_groups / sessions; set agent_provider to opencode there.
-# OpenCode SDK: Zen as the upstream provider + models under opencode/…
 OPENCODE_PROVIDER=opencode
 OPENCODE_MODEL=opencode/big-pickle
 OPENCODE_SMALL_MODEL=opencode/big-pickle
-
-# Point the credential proxy at Zen's Anthropic-compatible base URL (host + OneCLI must forward this host).
 ANTHROPIC_BASE_URL=https://opencode.ai/zen/v1
 ```
 
@@ -162,8 +206,6 @@ onecli secrets create --name "OpenCode Zen" --type generic \
   --header-name "x-api-key" --value-format "{value}"
 ```
 
-For comparison, OpenRouter uses `Authorization` + `Bearer {value}`. Zen is different by design.
-
 ### Per group / per session
 
 Schema: **`agent_groups.agent_provider`** and **`sessions.agent_provider`**. Set to `opencode` for groups or sessions that should use OpenCode. The container receives `AGENT_PROVIDER` from the resolved value (session overrides group).
@@ -173,7 +215,7 @@ Extra MCP servers still come from **`NANOCLAW_MCP_SERVERS`** / `container_config
 ## Operational notes
 
 - OpenCode keeps a local **`opencode serve`** process and SSE subscription; the provider tears down with **`stream.return`** and **SIGKILL** on the server process on **`abort()`** / shared runtime reset to avoid MCP/zombie hangs.
-- Session continuation is opaque (`ses_*` ids); stale sessions are cleared using **`isSessionInvalid`** on OpenCode-specific errors (timeouts, connection resets, not-found patterns) in addition to the poll-loop's existing recovery.
+- Session continuation uses UUID format (SDK 1.4.x / CLI 1.4.x). Stale sessions are cleared by `isSessionInvalid` on OpenCode-specific error patterns. If you see UUID-related errors after an accidental CLI upgrade, clear `session_state` in `outbound.db` and wipe the `opencode-xdg` directory under the session folder.
 - **`NO_PROXY`** for localhost matters when the OpenCode client talks to `127.0.0.1` inside the container while HTTP(S)_PROXY is set (e.g. OneCLI).
 
 ## Verify
PATCH

echo "Gold patch applied."
