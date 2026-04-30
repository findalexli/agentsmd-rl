#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xurl

# Idempotency guard
if grep -qF "description: A curl-like CLI tool for making authenticated requests to the X (Tw" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: xurl
+description: A curl-like CLI tool for making authenticated requests to the X (Twitter) API. Use this skill when you need to post tweets, reply, quote, search, read posts, manage followers, send DMs, upload media, or interact with any X API v2 endpoint. Supports OAuth 2.0, OAuth 1.0a, and app-only auth.
+---
+
 # xurl — Agent Skill Reference
 
 `xurl` is a CLI tool for the X API. It supports both **shortcut commands** (human/agent‑friendly one‑liners) and **raw curl‑style** access to any v2 endpoint. All commands return JSON to stdout.
PATCH

echo "Gold patch applied."
