#!/usr/bin/env bash
set -euo pipefail

cd /workspace/everclaw-community-branches

# Idempotency guard
if grep -qF "The proxy (port 8083) auto-opens blockchain sessions, auto-renews before expiry," "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -31,6 +31,37 @@ Access Kimi K2.5, Qwen3, GLM-4, Llama 3.3, and 10+ models with inference you own
 6. When the session ends, your **MOR is returned** (minus tiny usage fees)
 7. Re-stake the returned MOR into new sessions → persistent inference you own
 
+## Agent Integration (Recommended Path)
+
+**If you are an AI agent (OpenClaw, Claude, etc.), use the OpenAI-compatible proxy for all Morpheus inference. Do NOT use the bash scripts (session.sh, chat.sh) -- the proxy handles sessions, auth, and model routing automatically.**
+
+### Send Inference
+
+```bash
+curl http://127.0.0.1:8083/v1/chat/completions \
+  -H "Content-Type: application/json" \
+  -H "Authorization: Bearer morpheus-local" \
+  -d '{"model": "kimi-k2.5", "messages": [{"role": "user", "content": "Hello"}], "stream": false}'
+```
+
+### List Available Models
+
+```bash
+curl http://127.0.0.1:8083/v1/models
+```
+
+### Health Check
+
+```bash
+curl http://127.0.0.1:8083/health
+```
+
+The proxy (port 8083) auto-opens blockchain sessions, auto-renews before expiry, and injects all required auth headers. The bash scripts (`session.sh`, `chat.sh`) are available for manual debugging but should not be used for agent integration.
+
+See Section 12 for full proxy documentation.
+
+---
+
 ## Getting MOR Tokens
 
 You need MOR on Base to stake for inference. If you already have ETH, USDC, or USDT on Base:
PATCH

echo "Gold patch applied."
