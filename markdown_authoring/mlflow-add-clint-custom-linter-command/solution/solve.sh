#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "uv run clint .                    # Run MLflow custom linter" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -87,6 +87,9 @@ yarn --cwd mlflow/server/js test
 uv run ruff check . --fix         # Lint with auto-fix
 uv run ruff format .              # Format code
 
+# Custom MLflow linting with Clint
+uv run clint .                    # Run MLflow custom linter
+
 # Check for MLflow spelling typos
 uv run bash dev/mlflow-typo.sh .
 
PATCH

echo "Gold patch applied."
