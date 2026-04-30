#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "uv run --project ./src/integrations/<name> <cmd>   # Run against a local integra" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -39,10 +39,11 @@ uv sync                                # Install all dev dependencies
 just install                           # Same as above, plus perf group
 
 # Running code
-uv run -s my_script.py                 # Run a script with an editable prefect install
-uv run --extra aws repros/1234.py      # Run repro needing an integration extra
-prefect server start                   # Start local server
-prefect config view                    # Inspect current configuration
+uv run -s my_script.py                             # Run a script with an editable prefect install
+uv run --extra aws repros/1234.py                  # Run repro needing an integration extra
+uv run --project ./src/integrations/<name> <cmd>   # Run against a local integration from repo root
+prefect server start                               # Start local server
+prefect config view                                # Inspect current configuration
 
 # Testing (see tests/AGENTS.md for full details)
 uv run pytest tests/path.py -k name    # Run specific test
PATCH

echo "Gold patch applied."
