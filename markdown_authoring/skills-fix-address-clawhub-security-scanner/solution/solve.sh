#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "> **`auto_proceed: true` is intentional.** The HeyGen Video Agent API pauses at " "heygen-video/SKILL.md" && grep -qF "-H \"X-Api-Key: $HEYGEN_API_KEY\" | jq '.data.avatar_list[:5] | .[] | {avatar_id: " "platforms/nanoclaw/heygen/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/heygen-video/SKILL.md b/heygen-video/SKILL.md
@@ -30,23 +30,23 @@ metadata:
 
 ## Preamble (run first)
 
+No auto-run steps. Check for updates manually when desired:
 ```bash
-_SKILL_DIR="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)"
-_UPD=$("${_SKILL_DIR}/scripts/update-check.sh" 2>/dev/null || true)
-[ -n "$_UPD" ] && echo "$_UPD" || true
+"${SKILL_DIR}/scripts/update-check.sh"
 ```
-
-If output shows `UPGRADE_AVAILABLE <old> <new>`: tell the user "HeyGen Skills update available (v{old} → v{new}). Run `cd <skill-dir> && git pull` to update." Then continue with the skill normally.
-
-If output shows `JUST_UPGRADED <old> <new>`: tell the user "Running HeyGen Skills v{new} (just updated!)" and continue.
+This script is opt-in only. Do not execute it automatically on skill invocation.
 
 # HeyGen Video Producer
 
 You are a video producer. Not a form. Not an API wrapper. A producer who understands what makes video work and guides the user from idea to finished cut.
 
 **API Docs:** https://developers.heygen.com/docs/quick-start — All endpoints are v3. Base: `https://api.heygen.com`.
 
-**API Key Resolution:** Check `$HEYGEN_API_KEY` env var first. If not set, run `source ~/.heygen/config 2>/dev/null`. If still unset, tell the user to run `./setup` or `export HEYGEN_API_KEY=<key>`.
+**API Key Resolution:** Check `$HEYGEN_API_KEY` env var first. If not set, read it safely:
+```bash
+export HEYGEN_API_KEY=$(grep -m1 '^HEYGEN_API_KEY=' ~/.heygen/config 2>/dev/null | cut -d= -f2-)
+```
+Do not `source` the config file. If still unset, tell the user to run `./setup` or `export HEYGEN_API_KEY=<key>`.
 
 **Required headers on every API request — no exceptions:**
 ```
@@ -485,7 +485,7 @@ Before spawning any subagent, assemble the full request payload as a JSON object
 }
 ```
 
-> `auto_proceed: true` skips the interactive review checkpoint and goes straight to generation. Always include it.
+> **`auto_proceed: true` is intentional.** The HeyGen Video Agent API pauses at an interactive review checkpoint by default; without this flag, videos never complete. This is a known API behavior, not a security bypass — generation still requires explicit user request and a valid API key. No content is generated without user-initiated invocation of this skill.
 This payload is the handoff to any subagent. The subagent receives a finished payload — it does NOT modify the prompt, does NOT re-run Frame Check, does NOT look up avatar IDs.
 
 **Step 3: Subagent spawn pattern (for batch or non-blocking generation)**
diff --git a/platforms/nanoclaw/heygen/SKILL.md b/platforms/nanoclaw/heygen/SKILL.md
@@ -17,16 +17,16 @@ NOT for: image generation, audio-only TTS, video translation, or cinematic b-rol
 ### Step 1: Discover Available Avatars
 
 ```bash
-curl -s -X GET "https://api.heygen.com/v2/avatars" \
-  -H "X-Api-Key: $HEYGEN_API_KEY" | jq '.data.avatars[:5] | .[] | {avatar_id, avatar_name}'
+curl -s -X GET "https://api.heygen.com/v3/avatars" \
+  -H "X-Api-Key: $HEYGEN_API_KEY" | jq '.data.avatar_list[:5] | .[] | {avatar_id: .avatar_group_id, avatar_name}'
 ```
 
 Pick an avatar_id. If the user has a specific avatar, use that ID.
 
 ### Step 2: Find a Voice
 
 ```bash
-curl -s -X GET "https://api.heygen.com/v2/voices" \
+curl -s -X GET "https://api.heygen.com/v3/voices" \
   -H "X-Api-Key: $HEYGEN_API_KEY" | jq '.data.voices[:10] | .[] | {voice_id, display_name, language}'
 ```
 
PATCH

echo "Gold patch applied."
