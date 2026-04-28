#!/usr/bin/env bash
set -euo pipefail

cd /workspace/surrealdb

# Idempotency guard
if grep -qF "- When formatting or linting produces changes after a commit, create a new follo" ".cursor/rules/git-safety.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/git-safety.mdc b/.cursor/rules/git-safety.mdc
@@ -0,0 +1,22 @@
+---
+alwaysApply: true
+---
+
+# Git safety rules
+
+## Commits
+
+- Never amend a commit that has already been pushed to a remote, unless specifically requested. Always create a new commit instead.
+- Never amend a commit unless the user explicitly asks for it.
+- When formatting or linting produces changes after a commit, create a new follow-up commit (e.g. "Format code") rather than amending.
+
+## Pushing
+
+- Never force-push (`--force`, `--force-with-lease`, or any variant) unless the user explicitly asks for it.
+- Always use a regular `git push` after creating new commits.
+
+## General
+
+- Never run destructive or irreversible git commands (hard reset, branch deletion, etc.) unless explicitly requested.
+- Never modify git config.
+- When in doubt, ask before running any git command that could rewrite history.
PATCH

echo "Gold patch applied."
