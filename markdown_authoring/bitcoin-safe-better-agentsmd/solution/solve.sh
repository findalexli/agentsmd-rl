#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bitcoin-safe

# Idempotency guard
if grep -qF "- Before you commit, run pre-commit ruff format. commit and push the changes (us" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -3,8 +3,7 @@
 - Never use `getattr` or `setattr`;
 - use type hints
 - write clean code.  if you're writing many if statements you're probably doing it wrong.
-- run the pre-commit for all files before commiting and ensure that you fix all bugs to fulfill the pre-commit. For that to work you have to cd into the current project and activate the environment
-- commit and push the changes (use a dedicated branch for each session)
+- Before you commit, run pre-commit ruff format. commit and push the changes (use a dedicated branch for each session). If the pre-commit returns errors, fix them. For the pre-commit to work you have to cd into the current project and activate the environment.
 
 ## App run + GUI interaction notes
 - Launch the app with `DISPLAY=desktop:0 poetry run python -m bitcoin_safe`.
PATCH

echo "Gold patch applied."
