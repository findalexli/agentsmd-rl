#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cc-skills

# Idempotency guard
if grep -qF "description: Conventional Commits v1.0.0 branch naming, worktree naming, and com" "skills/conventional-git/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/conventional-git/SKILL.md b/skills/conventional-git/SKILL.md
@@ -1,12 +1,12 @@
 ---
 name: conventional-git
-description: Conventional Commits v1.0.0 branch naming and commit message standards for GitHub and GitLab projects. Use when creating branches, writing commits, generating commit messages, reviewing branch conventions, or setting up changelog automation. Apply when your project needs consistent git history, SemVer-driven releases, parseable changelog generation, or automatic issue closing.
+description: Conventional Commits v1.0.0 branch naming, worktree naming, and commit message standards for GitHub and GitLab projects. Use when creating branches, naming worktrees, writing commits, generating commit messages, reviewing branch conventions, or setting up changelog automation. Apply when your project needs consistent git history, SemVer-driven releases, parseable changelog generation, or automatic issue closing. Trigger when the user asks how to name a worktree, create a git worktree, or organize worktrees alongside branches.
 user-invocable: true
 license: MIT
 compatibility: Designed for Claude Code or similar AI coding agents. Requires git.
 metadata:
   author: samber
-  version: "1.1.0"
+  version: "1.2.0"
   openclaw:
     emoji: "📝"
     homepage: https://github.com/samber/cc-skills
@@ -37,6 +37,26 @@ Prefix with the issue number when one exists — GitHub and GitLab auto-link it
 
 NEVER include `worktree` in a branch name — git worktrees are a local checkout mechanism, not a branch concept; the name would leak implementation details into the remote and confuse other contributors.
 
+## Worktree Naming
+
+Worktrees are local checkout directories — they never appear in the remote. Place them under `.claude/worktrees/` and name them by replacing the branch `/` separator with `-`.
+
+```
+git worktree add .claude/worktrees/feat-user-authentication feat/user-authentication
+git worktree add .claude/worktrees/fix-87-login-race-condition fix/87-login-race-condition
+```
+
+The directory name mirrors the branch name so `git worktree list` stays readable and each worktree is immediately traceable to its branch without inspecting the checkout. Run `git worktree list` before creating a new one — reuse an existing worktree if it already covers the same branch.
+
+Keep worktrees scoped to a single branch. Doing unrelated work inside someone else's worktree obscures which changes belong where and makes cleanup error-prone.
+
+Remove the worktree once its branch is merged — either after a local merge or after the pull/merge request is closed on the remote. Stale worktrees accumulate and make `git worktree list` unreadable.
+
+```bash
+git worktree remove .claude/worktrees/feat-user-authentication   # branch merged locally
+git worktree prune                                                # remove refs to already-deleted directories
+```
+
 ## Commit Message Format
 
 ```
PATCH

echo "Gold patch applied."
