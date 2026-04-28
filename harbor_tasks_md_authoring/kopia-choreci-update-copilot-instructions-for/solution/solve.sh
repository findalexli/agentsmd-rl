#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kopia

# Idempotency guard
if grep -qF "- Ensure there are tests that cover and exercise the new or changed functionalit" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -23,6 +23,9 @@
 - Acknowledge good patterns when you see them
 - Ask clarifying questions when code intent is unclear
 
+## Review Test Coverage
+- Ensure there are tests that cover and exercise the new or changed functionality
+
 Always prioritize security vulnerabilities and performance issues that could impact users.
 
 Always suggest changes to improve readability.
PATCH

echo "Gold patch applied."
