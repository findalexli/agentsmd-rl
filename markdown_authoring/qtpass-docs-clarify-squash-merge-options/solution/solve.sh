#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "Only force push to feature branches when absolutely necessary (e.g., resolving m" ".opencode/skills/qtpass-github/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/qtpass-github/SKILL.md b/.opencode/skills/qtpass-github/SKILL.md
@@ -53,8 +53,8 @@ git remote add upstream https://github.com/IJHack/QtPass.git
 git fetch upstream
 git pull upstream main --rebase
 
-# Force push if needed
-git push -f
+# Force push if needed (safer)
+git push --force-with-lease <push-remote> <branch>
 ```
 
 This prevents "branch is out-of-date with base branch" errors.
@@ -88,15 +88,37 @@ git push -u origin new-branch-name
 
 Squash merging keeps the main branch history clean and avoids cluttering it with numerous intermediate commits from review iterations.
 
+### Squash merge now via GitHub CLI
+
+When all CI checks pass and you want to merge immediately:
+
 ```bash
-# Squash merge via GitHub CLI
-gh pr merge <PR_NUMBER> --squash --auto --delete-branch --subject "fix: description"
+# Squash merge immediately (all checks passed)
+gh pr merge <PR_NUMBER> --squash --delete-branch --subject "fix: description"
+```
 
-# Or with auto-merge (waits for CI)
+### Schedule squash merge (waits for CI)
+
+When you want to wait for CI to pass before merging:
+
+```bash
+# Squash merge that waits for CI checks to pass
 gh pr merge <PR_NUMBER> --squash --auto --delete-branch
 ```
 
-**Avoid force pushing to shared branches** - Only force push to feature branches when absolutely necessary (e.g., resolving merge conflicts, cleaning up commits). Never force push to main or branches that others may be working from.
+**Avoid force pushing to shared branches**
+
+Only force push to feature branches when absolutely necessary (e.g., resolving merge conflicts, cleaning up commits). Prefer `--force-with-lease` over `-f` because it fails if someone else pushed to the branch, preventing accidental overwrites of others' work. Never use `-f` or `--force` on main or shared branches:
+
+```bash
+# Safe force push (recommended)
+git push --force-with-lease <push-remote> <branch>
+
+# Never use on main or shared branches
+git push --force origin main  # AVOID THIS
+```
+
+Never force push to main or branches that others may be working from.
 
 **Merge strategies:**
 
@@ -286,8 +308,8 @@ git rebase upstream/main
 git add <resolved-files>
 git rebase --continue
 
-# Force push (since we rewrote history)
-git push -f
+# Force push (since we rewrote history; safer)
+git push --force-with-lease <push-remote> <branch>
 ```
 
 ## Fork Workflow
@@ -316,7 +338,7 @@ Note: When working with forks, use `myfork` for pushing and `upstream` for synci
 ```bash
 git checkout <branch-name>
 git pull upstream main --rebase
-git push -f
+git push --force-with-lease <push-remote> <branch-name>
 ```
 
 ### Merge Failed
@@ -452,5 +474,5 @@ act push -W .github/workflows/linter.yml -j build
 git fetch upstream
 git checkout <branch>
 git pull upstream main --rebase
-git push -f
+git push --force-with-lease <push-remote> <branch>
 ```
PATCH

echo "Gold patch applied."
