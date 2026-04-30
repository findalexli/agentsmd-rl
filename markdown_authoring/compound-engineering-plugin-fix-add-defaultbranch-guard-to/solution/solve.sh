#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "1. If on `main`, `master`, or the resolved default branch from Step 1, create a " "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md" && grep -qF "If the current branch matches `main`, `master`, or the resolved default branch n" "plugins/compound-engineering/skills/git-commit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -18,8 +18,17 @@ command git status
 command git diff HEAD
 command git branch --show-current
 command git log --oneline -10
+command git rev-parse --abbrev-ref origin/HEAD
 ```
 
+The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:
+
+```bash
+command gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
+```
+
+If both fail, fall back to `main`.
+
 If there are no changes, report that and stop.
 
 ### Step 2: Determine conventions
@@ -47,7 +56,7 @@ Interpret the result:
 
 ### Step 4: Branch, stage, and commit
 
-1. If on `main` or the repo's default branch, create a descriptive feature branch first (`command git checkout -b <branch-name>`). Derive the branch name from the change content.
+1. If on `main`, `master`, or the resolved default branch from Step 1, create a descriptive feature branch first (`command git checkout -b <branch-name>`). Derive the branch name from the change content.
 2. Before staging everything together, scan the changed files for naturally distinct concerns. If modified files clearly group into separate logical changes (e.g., a refactor in one set of files and a new feature in another), create separate commits for each group. Keep this lightweight -- group at the **file level only** (no `git add -p`), split only when obvious, and aim for two or three logical commits at most. If it's ambiguous, one commit is fine.
 3. Stage relevant files by name. Avoid `git add -A` or `git add .` to prevent accidentally including sensitive files.
 4. Commit following the conventions from Step 2. Use a heredoc for the message.
diff --git a/plugins/compound-engineering/skills/git-commit/SKILL.md b/plugins/compound-engineering/skills/git-commit/SKILL.md
@@ -18,10 +18,21 @@ command git status
 command git diff HEAD
 command git branch --show-current
 command git log --oneline -10
+command git rev-parse --abbrev-ref origin/HEAD
 ```
 
+The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:
+
+```bash
+command gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
+```
+
+If both fail, fall back to `main`.
+
 If there are no changes (nothing staged, nothing modified), report that and stop.
 
+If the current branch matches `main`, `master`, or the resolved default branch name, warn the user and ask whether to continue committing here or create a feature branch first. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply before proceeding. If the user chooses to create a branch, derive the name from the change content and switch to it before continuing.
+
 ### Step 2: Determine commit message convention
 
 Follow this priority order:
PATCH

echo "Gold patch applied."
