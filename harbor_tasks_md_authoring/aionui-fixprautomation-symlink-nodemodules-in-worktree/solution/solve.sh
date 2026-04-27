#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aionui

# Idempotency guard
if grep -qF "ln -s \"$REPO_ROOT/node_modules\" \"$WORKTREE_DIR/node_modules\"" ".claude/skills/pr-automation/SKILL.md" && grep -qF "After creating the worktree (all three paths), symlink `node_modules` so lint/ts" ".claude/skills/pr-fix/SKILL.md" && grep -qF "# Symlink node_modules so lint/tsc/test can run in the worktree" ".claude/skills/pr-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-automation/SKILL.md b/.claude/skills/pr-automation/SKILL.md
@@ -427,6 +427,10 @@ git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || true
 # Create worktree on the PR's head branch
 git fetch origin <head_branch>
 git worktree add "$WORKTREE_DIR" origin/<head_branch>
+
+# Symlink node_modules so tsc/lint can run in the worktree
+ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"
+
 cd "$WORKTREE_DIR"
 git checkout <head_branch>
 git rebase origin/<base_branch>
diff --git a/.claude/skills/pr-fix/SKILL.md b/.claude/skills/pr-fix/SKILL.md
@@ -166,6 +166,12 @@ git checkout bot/fix-pr-<PR_NUMBER>
 git merge --no-ff --no-edit FETCH_HEAD
 ```
 
+After creating the worktree (all three paths), symlink `node_modules` so lint/tsc/test can run:
+
+```bash
+ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"
+```
+
 Save `REPO_ROOT` and `WORKTREE_DIR` for later steps. All file reads, edits, lint, and test commands from this point forward run inside `WORKTREE_DIR`.
 
 ---
diff --git a/.claude/skills/pr-review/SKILL.md b/.claude/skills/pr-review/SKILL.md
@@ -169,6 +169,9 @@ git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || true
 # Fetch PR head and create detached worktree
 git fetch origin pull/${PR_NUMBER}/head
 git worktree add "$WORKTREE_DIR" FETCH_HEAD --detach
+
+# Symlink node_modules so lint/tsc/test can run in the worktree
+ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"
 ```
 
 Save `REPO_ROOT` and `WORKTREE_DIR` for use in subsequent steps. All file reads, lint, and diff commands from this point forward run inside `WORKTREE_DIR`.
PATCH

echo "Gold patch applied."
