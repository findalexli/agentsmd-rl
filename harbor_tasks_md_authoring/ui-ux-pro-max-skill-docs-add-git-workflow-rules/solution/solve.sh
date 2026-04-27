#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ui-ux-pro-max-skill

# Idempotency guard
if grep -qF "1. Create a new branch: `git checkout -b feat/... ` or `fix/...`" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -56,3 +56,12 @@ When modifying files, keep all agent workflows in sync:
 ## Prerequisites
 
 Python 3.x (no external dependencies required)
+
+## Git Workflow
+
+Never push directly to `main`. Always:
+
+1. Create a new branch: `git checkout -b feat/... ` or `fix/...`
+2. Commit changes
+3. Push branch: `git push -u origin <branch>`
+4. Create PR: `gh pr create`
PATCH

echo "Gold patch applied."
