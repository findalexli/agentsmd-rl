#!/usr/bin/env bash
set -euo pipefail

cd /workspace/voicemode

# Idempotency guard
if grep -qF "- **Path mapping**: Tailscale strips the incoming path before forwarding, so you" ".claude/skills/voicemode/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/voicemode/SKILL.md b/.claude/skills/voicemode/SKILL.md
@@ -265,6 +265,51 @@ See [Call Routing](../../../docs/guides/agents/call-routing/) for comprehensive
 - [Voice Proxy](../../../docs/guides/agents/call-routing/proxy.md) - Relay pattern for agents without voice
 - [Call Routing Overview](../../../docs/guides/agents/call-routing/README.md) - All routing patterns
 
+## Sharing Voice Services Over Tailscale
+
+Expose local Whisper (STT) and Kokoro (TTS) to other devices on your Tailnet via HTTPS.
+
+### Why
+
+- Browsers require HTTPS for microphone access (e.g., VoiceMode Connect web app)
+- Tailscale serve provides automatic HTTPS with valid Let's Encrypt certificates for `*.ts.net` domains
+- Enables using your powerful local machine's GPU from any device on your Tailnet
+
+### Setup
+
+```bash
+# Expose TTS (Kokoro on port 8880)
+tailscale serve --bg --set-path /v1/audio/speech http://localhost:8880/v1/audio/speech
+
+# Expose STT (Whisper on port 2022)
+tailscale serve --bg --set-path /v1/audio/transcriptions http://localhost:2022/v1/audio/transcriptions
+
+# Verify configuration
+tailscale serve status
+
+# Reset all serve config
+tailscale serve reset
+```
+
+### Endpoints
+
+After setup, endpoints are available at:
+- **TTS:** `https://<hostname>.<tailnet>.ts.net/v1/audio/speech`
+- **STT:** `https://<hostname>.<tailnet>.ts.net/v1/audio/transcriptions`
+
+### Important Notes
+
+- **Path mapping**: Tailscale strips the incoming path before forwarding, so you MUST include the full path in the target URL
+- **Same-machine testing**: Traffic doesn't route through Tailscale locally — test from another Tailnet device
+- **Multiple paths**: You can configure different paths to different backends on the same or different machines
+- **CORS**: Kokoro has CORS configured to allow `https://app.voicemode.dev` origins
+
+### Use with VoiceMode Connect
+
+In the VoiceMode Connect web app settings (app.voicemode.dev/settings), set:
+- **TTS Endpoint**: `https://<hostname>.<tailnet>.ts.net`
+- **STT Endpoint**: `https://<hostname>.<tailnet>.ts.net`
+
 ## Documentation Index
 
 | Topic | Link |
PATCH

echo "Gold patch applied."
