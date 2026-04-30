#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "See @../.cursor/rules/docs.mdc for details on Shopify CLI architecture and conve" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -0,0 +1,2 @@
+See @../.cursor/rules/base.mdc for information on your desired behavior.
+See @../.cursor/rules/docs.mdc for details on Shopify CLI architecture and conventions.
PATCH

echo "Gold patch applied."
