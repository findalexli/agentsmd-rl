#!/usr/bin/env bash
set -euo pipefail

cd /workspace/datastoria

# Idempotency guard
if grep -qF "- The agent must receive explicit user approval after showing those file lists b" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -95,3 +95,9 @@ Before finishing, verify:
 ## Commit Rules
 - Only commit what you change
 - Before creating a PR at GitHub, list all changed files on the branch and wait for user confirmation.
+- Before listing changed files, run `git fetch origin master`.
+- PR creation is blocked until the agent shows `Changed files vs origin/master` for each branch.
+- The agent must receive explicit user approval after showing those file lists before running any `gh pr create` command.
+- Before pushing a branch, run `git fetch origin master`.
+- Push is blocked until the agent shows `Changed files vs origin/master` for each branch being pushed.
+- The agent must receive explicit user approval after showing those file lists before running any `git push` command.
PATCH

echo "Gold patch applied."
