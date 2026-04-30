#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skillport

# Idempotency guard
if grep -qF "compatibility: Requires git 2.17+ (for worktree support). Git 2.22+ recommended " ".skills/experimental/git-branch-cleanup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.skills/experimental/git-branch-cleanup/SKILL.md b/.skills/experimental/git-branch-cleanup/SKILL.md
@@ -5,6 +5,7 @@ description: |
   staleness, and remote tracking. Provides interactive selection with safety guards.
   Use when the user wants to clean up branches, delete old branches, organize Git branches,
   or asks about which branches can be safely deleted.
+compatibility: Requires git 2.17+ (for worktree support). Git 2.22+ recommended for `git branch --show-current`.
 ---
 
 # Git Branch Cleanup
@@ -53,6 +54,12 @@ git branch --no-merged "$BASE_BRANCH"
 # Branches whose upstream is gone (remote deleted)
 git branch -vv | grep -F ': gone]' || true
 
+# List worktrees (branches with '+' prefix in git branch -v have worktrees)
+git worktree list
+
+# Branches with worktrees ('+' prefix indicates worktree association)
+git branch -v | grep '^+' || true
+
 # Branches ahead of upstream (have unpushed commits)
 git for-each-ref refs/heads \
   --format='%(refname:short) %(upstream:trackshort)' \
@@ -68,6 +75,7 @@ Categorize branches by safety level:
 | **Merged (Safe)** | Already merged to base branch | Safe to delete |
 | **Gone Remote** | Remote branch deleted | Review recommended |
 | **Stale** | No commits for 30+ days | Needs review |
+| **Has Worktree** | Branch checked out in a worktree (`+` prefix in `git branch -v`) | Remove worktree first |
 | **Ahead of Upstream** | Has unpushed commits | ⚠️ Do not delete |
 | **Unmerged** | Active work in progress | Use caution |
 
@@ -128,6 +136,35 @@ git branch -d <branch-name>  # For merged branches
 git branch -D <branch-name>  # Force delete (unmerged)
 ```
 
+**For branches with worktrees**, remove the worktree first:
+
+```bash
+# Check if branch has a worktree
+git worktree list | grep "\\[$branch\\]"
+
+# Remove worktree before deleting branch
+git worktree remove --force /path/to/worktree
+git branch -D <branch-name>
+```
+
+**Bulk delete [gone] branches with worktree handling:**
+
+```bash
+# Process all [gone] branches, handling worktrees automatically
+git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
+  echo "Processing branch: $branch"
+  # Find and remove worktree if it exists
+  worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
+  if [ ! -z "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
+    echo "  Removing worktree: $worktree"
+    git worktree remove --force "$worktree"
+  fi
+  # Delete the branch
+  echo "  Deleting branch: $branch"
+  git branch -D "$branch"
+done
+```
+
 ## Commands Reference
 
 ```bash
@@ -154,6 +191,12 @@ git fetch --prune || echo "Warning: Could not reach remote. Using cached data."
 # List oldest branches (30+ days)
 git for-each-ref --sort=committerdate refs/heads/ \
   --format='%(committerdate:short) %(refname:short)' | head -20
+
+# Worktree commands
+git worktree list                              # List all worktrees
+git worktree remove /path/to/worktree          # Remove a worktree
+git worktree remove --force /path/to/worktree  # Force remove (even if dirty)
+git worktree prune                             # Clean up stale worktree refs
 ```
 
 ## Dry Run Mode
@@ -181,6 +224,7 @@ Before deletion, verify:
 - [ ] Not the current branch
 - [ ] Not a protected branch (base/main/master/trunk/develop)
 - [ ] No unpushed commits (ahead of upstream)
+- [ ] Worktree removed first (if branch has associated worktree)
 - [ ] User confirmation obtained
 
 ### Quick safety commands
@@ -194,4 +238,11 @@ git for-each-ref refs/heads \
 # For a specific branch, confirm it's not ahead of upstream (if upstream exists)
 # (Empty output => nothing unpushed)
 git log --oneline @{u}..HEAD 2>/dev/null || echo "No upstream configured for this branch"
+
+# Check if a branch has an associated worktree
+# ('+' prefix in git branch -v output indicates worktree)
+git branch -v | grep "^+" | awk '{print $2}'
+
+# Find worktree path for a specific branch
+git worktree list | grep "\\[branch-name\\]"
 ```
PATCH

echo "Gold patch applied."
