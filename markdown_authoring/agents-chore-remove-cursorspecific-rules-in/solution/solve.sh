#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF ".cursor/rules/adding-documentation.mdc" ".cursor/rules/adding-documentation.mdc" && grep -qF ".cursor/rules/test-no-watch.mdc" ".cursor/rules/test-no-watch.mdc" && grep -qF ".cursor/rules/use-pnpm.mdc" ".cursor/rules/use-pnpm.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/adding-documentation.mdc b/.cursor/rules/adding-documentation.mdc
@@ -1,4 +0,0 @@
----
-alwaysApply: true
----
-If you are adding a markdownfile that is documentation, make sure to add it in the correct contextual place in the main README.md file rather than a separate file nested in some directory.
\ No newline at end of file
diff --git a/.cursor/rules/test-no-watch.mdc b/.cursor/rules/test-no-watch.mdc
@@ -1,12 +0,0 @@
----
-alwaysApply: true
----
-# Test Commands Without Watch Mode
-
-When running tests, use the `--run` flag to avoid watch mode:
-
-- `pnpm test --run` - Run all tests once and exit
-- `pnpm test --run src/__tests__/agents/` - Run specific directory tests once and exit  
-- `pnpm test --run <specific-test-file>` - Run specific test file once and exit
-
-This prevents tests from getting stuck in watch mode where you need to press 'q' to quit.
diff --git a/.cursor/rules/use-pnpm.mdc b/.cursor/rules/use-pnpm.mdc
@@ -1,6 +0,0 @@
----
-description: 
-globs: 
-alwaysApply: true
----
-Use pnpm as a package manager instead of yarn, bun, or npm.
\ No newline at end of file
PATCH

echo "Gold patch applied."
