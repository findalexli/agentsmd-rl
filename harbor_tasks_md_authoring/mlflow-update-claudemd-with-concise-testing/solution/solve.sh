#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "uv run --with transformers pytest tests/transformers" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -74,6 +74,10 @@ uv run pytest tests/
 # Run specific test file
 uv run pytest tests/test_version.py
 
+# Run tests with optional dependencies/extras
+uv run --with transformers pytest tests/transformers
+uv run --extra gateway pytest tests/gateway
+
 # Run JavaScript tests
 yarn --cwd mlflow/server/js test
 ```
PATCH

echo "Gold patch applied."
