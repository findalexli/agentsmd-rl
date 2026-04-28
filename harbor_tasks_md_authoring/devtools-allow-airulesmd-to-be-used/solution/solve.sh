#!/usr/bin/env bash
set -euo pipefail

cd /workspace/devtools

# Idempotency guard
if grep -qF "description: Apply rules from AI_RULES.md to all interactions." ".cursor/rules/ai_rules.mdc" && grep -qF "Refer to the shared [AI Rules](AI_RULES.md) for guidelines when working in this " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/ai_rules.mdc b/.cursor/rules/ai_rules.mdc
@@ -0,0 +1,8 @@
+---
+description: Apply rules from AI_RULES.md to all interactions.
+globs: "*"
+alwaysApply: true
+---
+# AI Rules
+
+Follow the rules defined in [AI_RULES.md](../../AI_RULES.md).
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,3 @@
+# Claude Code Guidelines
+
+Refer to the shared [AI Rules](AI_RULES.md) for guidelines when working in this repository.
PATCH

echo "Gold patch applied."
