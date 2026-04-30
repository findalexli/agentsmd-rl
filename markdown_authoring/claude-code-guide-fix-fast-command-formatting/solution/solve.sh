#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-guide

# Idempotency guard
if grep -qF "| `/fast [on\\|off]` | Toggle fast mode on or off |" "skills/guide/ask/references/built-ins.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/guide/ask/references/built-ins.md b/skills/guide/ask/references/built-ins.md
@@ -32,7 +32,7 @@ Type `/` in Claude Code to see all available commands. Some commands depend on y
 | `/cost` | Show token usage statistics |
 | `/usage` | Show plan usage limits and rate limit status |
 | `/doctor` | Diagnose and verify your Claude Code installation |
-| `/fast [on|off]` | Toggle fast mode on or off |
+| `/fast [on\|off]` | Toggle fast mode on or off |
 
 ### Tools & Integrations
 
PATCH

echo "Gold patch applied."
