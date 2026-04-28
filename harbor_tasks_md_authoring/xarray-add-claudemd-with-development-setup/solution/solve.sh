#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xarray

# Idempotency guard
if grep -qF "uv run pytest xarray/tests/test_dataarray.py  # Specific file" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,21 @@
+# xarray development setup
+
+## Setup
+
+```bash
+uv sync
+```
+
+## Run tests
+
+```bash
+uv run pytest xarray -n auto  # All tests in parallel
+uv run pytest xarray/tests/test_dataarray.py  # Specific file
+```
+
+## Linting & type checking
+
+```bash
+pre-commit run --all-files  # Includes ruff and other checks
+uv run dmypy run  # Type checking with mypy
+```
PATCH

echo "Gold patch applied."
