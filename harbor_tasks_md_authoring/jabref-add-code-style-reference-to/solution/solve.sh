#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jabref

# Idempotency guard
if grep -qF "- Follow JabRef's code style rules as documented in [docs/getting-into-the-code/" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -56,6 +56,7 @@ Agents **must not**:
 - Match naming conventions exactly
 - Keep methods small and focused
 - Avoid premature abstractions
+- Follow JabRef's code style rules as documented in [docs/getting-into-the-code/guidelines-for-setting-up-a-local-workspace/intellij-13-code-style.md](docs/getting-into-the-code/guidelines-for-setting-up-a-local-workspace/intellij-13-code-style.md)
 
 ---
 
PATCH

echo "Gold patch applied."
