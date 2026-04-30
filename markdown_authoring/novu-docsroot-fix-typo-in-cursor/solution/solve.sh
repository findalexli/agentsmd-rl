#!/usr/bin/env bash
set -euo pipefail

cd /workspace/novu

# Idempotency guard
if grep -qF "- Do not attempt to build or run the dashboard as the user will be already runni" ".cursor/rules/dashboard.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/dashboard.mdc b/.cursor/rules/dashboard.mdc
@@ -3,6 +3,6 @@ description:
 globs: apps/dashboard/**/*
 alwaysApply: false
 ---
-- Do not attempt to to build or run the dashboard as the user will be already running it, to check types you should be able to access the eslint results in cursor.
+- Do not attempt to build or run the dashboard as the user will be already running it, to check types you should be able to access the eslint results in cursor.
 - Use lowercase with dashes for directories and files (e.g., components/auth-wizard).
 - Favor named exports for components.
PATCH

echo "Gold patch applied."
