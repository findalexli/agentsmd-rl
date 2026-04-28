#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lxd

# Idempotency guard
if grep -qF "- Use **US English spelling** throughout all user-facing text, including documen" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -208,6 +208,17 @@ For error message assertions, prefer single-quoted strings so error text with `"
 
 <!-- END COMMIT STRUCTURE -->
 
+### Language and Spelling
+
+- Use **US English spelling** throughout all user-facing text, including documentation, CLI output, and error messages. Common examples:
+  - `behavior` not `behaviour`
+  - `color` not `colour`
+  - `center` not `centre`
+  - `license` not `licence`
+  - `initialize` not `initialise`
+  - `analyze` not `analyse`
+  - `canceled` not `cancelled`
+
 ### Code Style
 
 - Follow `golangci-lint` rules (see `.golangci.yaml`)
PATCH

echo "Gold patch applied."
