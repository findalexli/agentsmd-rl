#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "# Fetch (via pull) and rebase on main" ".opencode/skills/qtpass-github/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/qtpass-github/SKILL.md b/.opencode/skills/qtpass-github/SKILL.md
@@ -49,8 +49,7 @@ gh pr create --base main --title "Fix" --body "Fixes #issue"
 ```bash
 # If upstream remote is not set, add it (one-time setup):
 git remote add upstream https://github.com/IJHack/QtPass.git
-# Fetch and rebase on main
-git fetch upstream
+# Fetch (via pull) and rebase on main
 git pull upstream main --rebase
 
 # Force push if needed (safer)
@@ -299,9 +298,9 @@ gh run view <RUN_ID> --job <JOB_NAME> --log
 When branch is behind main and has conflicts:
 
 ```bash
-# Fetch and rebase
-git fetch upstream
+# Checkout, fetch, and rebase
 git checkout <branch>
+git fetch upstream
 git rebase upstream/main
 
 # Resolve conflicts in editor, then:
@@ -472,7 +471,6 @@ Before merging a PR:
 act push -W .github/workflows/linter.yml -j build
 
 # Update with latest main before merging
-git fetch upstream
 git checkout <branch>
 git pull upstream main --rebase
 git push --force-with-lease <push-remote> <branch>
PATCH

echo "Gold patch applied."
