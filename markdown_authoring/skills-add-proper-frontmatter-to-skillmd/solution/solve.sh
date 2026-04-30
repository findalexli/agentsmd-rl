#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: Build, debug, and optimize Claude API / Anthropic SDK apps. Apps bu" "skills/claude-api/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/claude-api/SKILL.md b/skills/claude-api/SKILL.md
@@ -1,3 +1,10 @@
+---
+name: claude-api
+description: Build, debug, and optimize Claude API / Anthropic SDK apps. Apps built with this skill should include prompt caching. TRIGGER when: code imports anthropic/@anthropic-ai/sdk; user asks to use the Claude API, Anthropic SDKs, or Managed Agents (/v1/agents, /v1/sessions, /v1/environments). DO NOT TRIGGER when: code imports `openai`/other AI SDK, general programming, or ML/data-science tasks.
+license: Complete terms in LICENSE.txt
+---
+
+
 # Building LLM-Powered Applications with Claude
 
 This skill helps you build LLM-powered applications with Claude. Choose the right surface based on your needs, detect the project language, then read the relevant language-specific documentation.
PATCH

echo "Gold patch applied."
