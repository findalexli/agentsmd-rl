#!/usr/bin/env bash
set -euo pipefail

cd /workspace/docs

# Idempotency guard
if grep -qF "- Troubleshooting covers the most common errors and provides direct solutions" ".cursor/rules/docs-reader-persona-junior-sysadmin.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/docs-reader-persona-junior-sysadmin.mdc b/.cursor/rules/docs-reader-persona-junior-sysadmin.mdc
@@ -46,7 +46,7 @@ When reviewing or iterating on documentation, evaluate it through the lens of th
 - Expected output or a success check is shown after key steps
 - Technical terms are briefly defined inline on first use
 - The "why" is explained in one sentence when it matters
-- Troubleshooting section covers the most common errors
+- Troubleshooting covers the most common errors and provides direct solutions
 
 ## How to Use This Persona When Reviewing Docs
 
PATCH

echo "Gold patch applied."
