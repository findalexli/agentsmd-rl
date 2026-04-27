#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- Place success/completion callbacks (e.g., `onDelete`, `onReset`) in `onSuccess" "ui-v2/src/components/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/src/components/AGENTS.md b/ui-v2/src/components/AGENTS.md
@@ -51,6 +51,11 @@ This directory contains React components for the Prefect UI migration from Vue t
 - NEVER use `React.FC`
 - NEVER use `as unknown` or `eslint-disable` comments
 
+## Mutation Error Handling
+
+- Use `toast.error(message)` to surface mutation errors to the user — never `console.error`
+- Place success/completion callbacks (e.g., `onDelete`, `onReset`) in `onSuccess`, **not** `onSettled` — `onSettled` fires on both success and failure, which closes dialogs before the user can see the error toast
+
 ## Testing
 
 - Use `vitest` and `@testing-library/react` for testing
PATCH

echo "Gold patch applied."
