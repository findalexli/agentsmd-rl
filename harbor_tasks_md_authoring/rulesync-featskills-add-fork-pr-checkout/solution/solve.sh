#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rulesync

# Idempotency guard
if grep -qF "- **\"refusing to fetch into branch checked out at...\"**: A worktree with that br" ".rulesync/skills/git-worktree-runner/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.rulesync/skills/git-worktree-runner/SKILL.md b/.rulesync/skills/git-worktree-runner/SKILL.md
@@ -3,7 +3,8 @@ name: git-worktree-runner
 description: >-
   Manages git worktrees using git-worktree-runner (gtr). Use when the user needs
   to create, list, remove, or navigate worktrees with `git gtr` commands, open
-  editors or AI tools in worktrees, or manage parallel development branches.
+  editors or AI tools in worktrees, manage parallel development branches, or
+  check out GitHub PRs (including from forks) into worktrees.
 targets:
   - "*"
 allowed-tools: "Bash(git-worktree-runner:*)"
@@ -161,3 +162,64 @@ git gtr new hotfix-critical -e
 git gtr rm hotfix-critical
 # Back to feature-branch work without context switching
 ```
+
+## Example: Checkout a Fork PR into Worktree
+
+For PRs from forked repositories, the branch is not on `origin`. Use GitHub's `refs/pull/<number>/head` ref to fetch it.
+
+### Procedure
+
+Given a PR number or URL:
+
+1. **Get PR metadata**
+
+   ```bash
+   gh pr view <PR_NUMBER> --json headRefName,isCrossRepository
+   ```
+
+2. **Check for existing worktree** with the same branch name
+
+   ```bash
+   git worktree list
+   ```
+
+   If it exists, remove it first: `git gtr rm <branch>`
+
+3. **Fetch the PR ref** into a local branch (use `--force` to handle diverged history from force-pushes)
+
+   ```bash
+   git fetch origin pull/<PR_NUMBER>/head:<BRANCH_NAME> --force
+   ```
+
+4. **Create the worktree** with `--track local` since it's a local-only branch
+
+   ```bash
+   git gtr new <BRANCH_NAME> --track local
+   ```
+
+5. **Verify**
+   ```bash
+   git gtr list
+   ```
+
+### Full example (PR #1223 from a fork)
+
+```bash
+gh pr view 1223 --json headRefName,isCrossRepository
+git fetch origin pull/1223/head:fix/comprehensive-file-formats-docs --force
+git gtr new fix/comprehensive-file-formats-docs --track local
+git gtr list
+```
+
+### Shortening long branch names
+
+```bash
+git fetch origin pull/1223/head:pr-1223 --force
+git gtr new pr-1223 --track local
+```
+
+### Common errors
+
+- **"refusing to fetch into branch checked out at..."**: A worktree with that branch exists. `git gtr rm <branch>` first.
+- **"non-fast-forward" rejected**: Local branch diverged. Add `--force` to the fetch.
+- **Both errors**: Remove the worktree first, then fetch with `--force`.
PATCH

echo "Gold patch applied."
