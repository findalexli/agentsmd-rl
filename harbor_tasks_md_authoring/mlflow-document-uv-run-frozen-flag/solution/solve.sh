#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "If PyPI is unreachable, add `--frozen` to `uv run` commands that should use the " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -78,6 +78,14 @@ tail -f /tmp/mlflow-dev-server.log
 
 ## Development Commands
 
+### Offline / No-Network Usage
+
+If PyPI is unreachable, add `--frozen` to `uv run` commands that should use the existing `uv.lock` as-is without modifying the environment. This works when the required dependencies are already installed or available in the local cache:
+
+```bash
+uv run --frozen pytest tests/
+```
+
 ### Testing
 
 ```bash
PATCH

echo "Gold patch applied."
