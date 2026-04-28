#!/usr/bin/env bash
set -euo pipefail

cd /workspace/surrealdb.py

# Idempotency guard
if grep -qF "This project uses `uv` for dependency management and includes several tools for " ".cursor/tooling.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/tooling.mdc b/.cursor/tooling.mdc
@@ -0,0 +1,68 @@
+---
+alwaysApply: true
+---
+
+# Development Tooling
+
+This project uses `uv` for dependency management and includes several tools for code quality and testing. These should always pass before a tasks is considered complete.
+
+## Setup
+
+Install dependencies:
+```bash
+uv sync --group dev
+```
+
+## Testing
+
+### Run All Tests
+```bash
+uv run pytest
+```
+
+### Run Specific Tests
+```bash
+uv run pytest tests/unit_tests/data_types/test_geometry.py
+```
+
+### Test Coverage
+Coverage reports are generated automatically when running tests. View the HTML report:
+```bash
+uv run pytest --cov=src/surrealdb --cov-report=term-missing --cov-report=html
+```
+
+## Code Quality
+
+### Format Code
+Check formatting:
+```bash
+uv run ruff format --check --diff src/
+```
+
+Apply formatting:
+```bash
+uv run ruff format src/
+```
+
+### Lint Code
+```bash
+uv run ruff check src/
+```
+
+## Type Checking
+
+### mypy
+Check library:
+```bash
+uv run mypy --explicit-package-bases src/
+```
+
+Check tests:
+```bash
+uv run mypy --explicit-package-bases tests/
+```
+
+### pyright
+```bash
+uv run pyright src/
+```
\ No newline at end of file
PATCH

echo "Gold patch applied."
