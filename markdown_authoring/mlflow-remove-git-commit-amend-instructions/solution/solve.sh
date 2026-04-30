#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -167,10 +167,6 @@ git commit -s -m "Your commit message"
 # Then check all files changed in your PR
 uv run --only-group lint pre-commit run --from-ref origin/master --to-ref HEAD
 
-# Fix any issues and amend your commit if needed
-git add <fixed files>
-git commit --amend -s
-
 # Re-run pre-commit to verify fixes
 uv run --only-group lint pre-commit run --from-ref origin/master --to-ref HEAD
 
PATCH

echo "Gold patch applied."
