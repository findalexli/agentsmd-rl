#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dippy

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,13 +0,0 @@
-# Dippy
-
-Shell command approval hook for AI coding assistants.
-
-## Commands
-
-```bash
-just test        # Run tests (Python 3.14)
-just test-all    # All Python versions (3.11-3.14)
-just lint        # Lint (ruff check)
-just fmt         # Format (ruff format)
-just check       # All of the above in parallel — MUST PASS before committing
-```
PATCH

echo "Gold patch applied."
