#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentguard

# Idempotency guard
if grep -qF "argument-hint: \"[scan|action|trust|report|config] [args...]\"" "skills/agentguard/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/agentguard/SKILL.md b/skills/agentguard/SKILL.md
@@ -3,7 +3,7 @@ name: agentguard
 description: GoPlus AgentGuard — AI agent security guard. Automatically blocks dangerous commands, prevents data leaks, and protects secrets. Use when reviewing third-party code, auditing skills, checking for vulnerabilities, evaluating action safety, or viewing security logs.
 user-invocable: true
 allowed-tools: Read, Grep, Glob, Bash(node *)
-argument-hint: [scan|action|trust|report|config] [args...]
+argument-hint: "[scan|action|trust|report|config] [args...]"
 ---
 
 # GoPlus AgentGuard — AI Agent Security Framework
PATCH

echo "Gold patch applied."
