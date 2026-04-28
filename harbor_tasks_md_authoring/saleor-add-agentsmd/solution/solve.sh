#!/usr/bin/env bash
set -euo pipefail

cd /workspace/saleor

# Idempotency guard
if grep -qF "- Prefer using fixtures over mocking. Fixtures are usually within directory \"tes" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,17 @@
+# AGENTS.md
+
+# Testing
+
+## Running tests
+
+- Run tests using `pytest`
+- Attach `--reuse-db` argument to speed up tests by reusing the test database
+- Select tests to run by passing test file path as an argument
+- Enter virtual environment before executing tests
+
+## Writing tests
+
+- Use given/when/then structure for clarity
+- Use `pytest` fixtures for setup and teardown
+- Declare test suites flat in file. Do not wrapp in classes
+- Prefer using fixtures over mocking. Fixtures are usually within directory "tests/fixtures" and are functions decorated with`@pytest.fixture`
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,14 +1 @@
-# Testing
-
-## Running tests
-
-- Run tests using `pytest`
-- Attach `--reuse-db` argument to speed up tests by reusing the test database
-- Select tests to run by passing test file path as an argument
-- Enter virtual environment before executing tests
-
-## Writing tests
-
-- Use given/when/then structure for clarity
-- Use `pytest` fixtures for setup and teardown
-- Declare test suites flat in file. Do not wrapp in classes
+@AGENTS.md
PATCH

echo "Gold patch applied."
