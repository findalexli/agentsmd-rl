#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aionui

# Idempotency guard
if grep -qF "# Create worktree on the PR's head branch; fetch base branch for accurate rebase" ".claude/skills/pr-automation/SKILL.md" && grep -qF "BASE_REF=$(gh pr view ${PR_NUMBER} --json baseRefName --jq '.baseRefName')" ".claude/skills/pr-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-automation/SKILL.md b/.claude/skills/pr-automation/SKILL.md
@@ -286,6 +286,7 @@ Otherwise, **compute merge gate** (using remote refs — no checkout needed):
 ```bash
 git fetch origin pull/${PR_NUMBER}/head
 BASE_REF=$(gh pr view <PR_NUMBER> --json baseRefName --jq '.baseRefName')
+git fetch origin "$BASE_REF"
 FILES_CHANGED=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only | wc -l | tr -d ' ')
 # CRITICAL_PATH_PATTERN: defined in Configuration section above
 HAS_CRITICAL=false
@@ -486,8 +487,9 @@ WORKTREE_DIR="/tmp/aionui-pr-${PR_NUMBER}"
 # Clean up any stale worktree
 git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || true
 
-# Create worktree on the PR's head branch
+# Create worktree on the PR's head branch; fetch base branch for accurate rebase
 git fetch origin <head_branch>
+git fetch origin <base_branch>
 git worktree add "$WORKTREE_DIR" origin/<head_branch>
 
 # Symlink node_modules so tsc/lint can run in the worktree
@@ -559,6 +561,7 @@ No checkout needed — use remote refs to check the diff:
 ```bash
 git fetch origin pull/${PR_NUMBER}/head
 BASE_REF=$(gh pr view <PR_NUMBER> --json baseRefName --jq '.baseRefName')
+git fetch origin "$BASE_REF"
 
 FILES_CHANGED=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only | wc -l | tr -d ' ')
 
diff --git a/.claude/skills/pr-review/SKILL.md b/.claude/skills/pr-review/SKILL.md
@@ -168,8 +168,10 @@ WORKTREE_DIR="/tmp/aionui-pr-${PR_NUMBER}"
 # Clean up any stale worktree from a previous crash
 git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || true
 
-# Fetch PR head and create detached worktree
+# Fetch PR head AND base branch so the three-dot diff is accurate
 git fetch origin pull/${PR_NUMBER}/head
+BASE_REF=$(gh pr view ${PR_NUMBER} --json baseRefName --jq '.baseRefName')
+git fetch origin "$BASE_REF"
 git worktree add "$WORKTREE_DIR" FETCH_HEAD --detach
 
 # Symlink node_modules so lint/tsc/test can run in the worktree
PATCH

echo "Gold patch applied."
