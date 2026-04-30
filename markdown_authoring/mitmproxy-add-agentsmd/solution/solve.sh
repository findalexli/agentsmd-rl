#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mitmproxy

# Idempotency guard
if grep -qF "- When adding new source files, additionally run: `uv run tox -e individual_cove" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,3 @@
+- This project uses uv. Always use `uv run pytest` and don't run pytest directly.
+- To run all tests: `uv run tox`.
+- When adding new source files, additionally run: `uv run tox -e individual_coverage -- FILENAME`.
\ No newline at end of file
PATCH

echo "Gold patch applied."
