#!/usr/bin/env bash
set -euo pipefail

cd /workspace/buildwithclaude

# Idempotency guard
if grep -qF "Register .com, .xyz, .org and 1000+ ICANN domains with cryptocurrency payments v" "plugins/all-skills/skills/lobsterdomains/SKILL.md" && grep -qF "AI-powered video editing for YouTube creators. Submit a raw recording URL, get b" "plugins/all-skills/skills/tubeify/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/all-skills/skills/lobsterdomains/SKILL.md b/plugins/all-skills/skills/lobsterdomains/SKILL.md
@@ -0,0 +1,45 @@
+---
+name: lobsterdomains
+category: web
+description: Register ICANN domains with crypto payments (USDC/USDT/ETH/BTC) via API — built for AI agents
+---
+
+# LobsterDomains
+
+Register .com, .xyz, .org and 1000+ ICANN domains with cryptocurrency payments via a simple REST API. Built for AI agents to acquire domains fully autonomously.
+
+## When to Use This Skill
+
+- User wants to check if a domain name is available
+- User wants to register a domain programmatically without browser interaction
+- User wants to pay for domain registration with crypto (USDC/USDT/ETH/BTC)
+
+## What This Skill Does
+
+1. Checks domain availability and live pricing
+2. Accepts on-chain payment (USDC/USDT on Ethereum, Arbitrum, Base, or Optimism)
+3. Registers the domain and returns DNS management credentials
+
+## Usage
+
+```bash
+# Check availability
+curl "https://lobsterdomains.xyz/api/v1/domains/check?domain=example.com" \
+  -H "Authorization: Bearer $LOBSTERDOMAINS_API_KEY"
+
+# Register after payment
+curl -X POST https://lobsterdomains.xyz/api/v1/domains/register \
+  -H "Authorization: Bearer $LOBSTERDOMAINS_API_KEY" \
+  -H "Content-Type: application/json" \
+  -d '{"domain":"example.com","tx_hash":"0x...","contact":{"name":"...","email":"..."}}'
+```
+
+## Setup
+
+Generate an API key at https://lobsterdomains.xyz/api-keys (requires Ethereum wallet auth).
+
+## Links
+
+- Website: https://lobsterdomains.xyz
+- ClawHub: https://clawhub.ai/esokullu/lobsterdomains
+- Full docs: https://lobsterdomains.xyz/skills.md
diff --git a/plugins/all-skills/skills/tubeify/SKILL.md b/plugins/all-skills/skills/tubeify/SKILL.md
@@ -0,0 +1,44 @@
+---
+name: tubeify
+category: media
+description: AI video editor for YouTube — removes pauses, filler words, and dead air from raw recordings via API
+---
+
+# Tubeify
+
+AI-powered video editing for YouTube creators. Submit a raw recording URL, get back a polished, trimmed video automatically — no manual editing required.
+
+## When to Use This Skill
+
+- User wants to remove dead air or pauses from a video recording
+- User wants to clean up filler words (um, uh, etc.) from a video
+- User wants to automate post-recording video editing for YouTube
+
+## What This Skill Does
+
+1. Authenticates to Tubeify with a wallet address
+2. Submits the raw video URL with processing options
+3. Polls for completion and returns a download link
+
+## Usage
+
+```bash
+# Authenticate
+curl -c session.txt -X POST https://tubeify.xyz/index.php \
+  -d "wallet=<YOUR_WALLET>"
+
+# Submit video
+curl -b session.txt -X POST https://tubeify.xyz/process.php \
+  -d "video_url=<URL>" \
+  -d "remove_pauses=true" \
+  -d "remove_fillers=true"
+
+# Check status
+curl -b session.txt https://tubeify.xyz/status.php
+```
+
+## Links
+
+- Website: https://tubeify.xyz
+- ClawHub: https://clawhub.ai/esokullu/tubeify
+- Full docs: https://tubeify.xyz/skills.md
PATCH

echo "Gold patch applied."
