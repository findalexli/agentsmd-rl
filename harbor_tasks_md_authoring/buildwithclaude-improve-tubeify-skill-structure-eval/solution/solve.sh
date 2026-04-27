#!/usr/bin/env bash
set -euo pipefail

cd /workspace/buildwithclaude

# Idempotency guard
if grep -qF "Submit a raw recording URL to the Tubeify API and get back a polished, trimmed v" "plugins/all-skills/skills/tubeify/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/all-skills/skills/tubeify/SKILL.md b/plugins/all-skills/skills/tubeify/SKILL.md
@@ -1,44 +1,92 @@
 ---
 name: tubeify
-category: media
-description: AI video editor for YouTube — removes pauses, filler words, and dead air from raw recordings via API
+description: >
+  Remove pauses, filler words (um, uh), and dead air from raw YouTube recordings
+  via the Tubeify API. Use when the user wants to edit a video, clean up audio,
+  trim silences, or polish a raw recording for YouTube.
 ---
 
 # Tubeify
 
-AI-powered video editing for YouTube creators. Submit a raw recording URL, get back a polished, trimmed video automatically — no manual editing required.
+Submit a raw recording URL to the Tubeify API and get back a polished, trimmed video with pauses, filler words, and dead air removed automatically.
 
-## When to Use This Skill
+## Workflow
 
-- User wants to remove dead air or pauses from a video recording
-- User wants to clean up filler words (um, uh, etc.) from a video
-- User wants to automate post-recording video editing for YouTube
+### 1. Authenticate
 
-## What This Skill Does
+```bash
+curl -c session.txt -X POST https://tubeify.xyz/index.php \
+  -d "wallet=<WALLET_ADDRESS>"
+```
+
+Response on success:
 
-1. Authenticates to Tubeify with a wallet address
-2. Submits the raw video URL with processing options
-3. Polls for completion and returns a download link
+```json
+{ "status": "ok", "session": "active" }
+```
 
-## Usage
+If the response contains `"status": "error"`, check the wallet address and retry.
 
-```bash
-# Authenticate
-curl -c session.txt -X POST https://tubeify.xyz/index.php \
-  -d "wallet=<YOUR_WALLET>"
+### 2. Submit video for processing
 
-# Submit video
+```bash
 curl -b session.txt -X POST https://tubeify.xyz/process.php \
   -d "video_url=<URL>" \
   -d "remove_pauses=true" \
   -d "remove_fillers=true"
+```
+
+Parameters:
+- `video_url` (required) — direct URL to the raw video file
+- `remove_pauses` — remove silent gaps and dead air (default: `true`)
+- `remove_fillers` — remove filler words like "um", "uh", "like" (default: `true`)
 
-# Check status
+Response on success:
+
+```json
+{ "status": "queued", "job_id": "abc123" }
+```
+
+### 3. Poll for completion
+
+```bash
 curl -b session.txt https://tubeify.xyz/status.php
 ```
 
+Poll every 15 seconds. Terminal states:
+
+| `status`   | Meaning                        | Action                        |
+|------------|--------------------------------|-------------------------------|
+| `queued`   | Waiting in queue               | Keep polling                  |
+| `processing` | Actively editing            | Keep polling                  |
+| `complete` | Finished — download ready      | Read `download_url` from body |
+| `failed`   | Processing error               | Check `error` field, retry    |
+
+Complete response example:
+
+```json
+{ "status": "complete", "download_url": "https://tubeify.xyz/dl/abc123.mp4" }
+```
+
+Failed response example:
+
+```json
+{ "status": "failed", "error": "Unsupported video format" }
+```
+
+### 4. Download the result
+
+```bash
+curl -o edited_video.mp4 "<download_url>"
+```
+
+## Environment
+
+| Variable | Description |
+|----------|-------------|
+| `TUBEIFY_WALLET` | Ethereum wallet address for authentication |
+
 ## Links
 
 - Website: https://tubeify.xyz
-- ClawHub: https://clawhub.ai/esokullu/tubeify
 - Full docs: https://tubeify.xyz/skills.md
PATCH

echo "Gold patch applied."
