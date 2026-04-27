#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "3. If any test or type-check command fails, inspect logs immediately, fix the is" ".agents/skills/push/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/push/SKILL.md b/.agents/skills/push/SKILL.md
@@ -11,9 +11,9 @@ If on a non-main branch where the existing PR is already merged, the uncommitted
 
 1. Checkout main and pull
 2. Create a new branch with a name describing the uncommitted changes
-3. Continue with the commit workflow below
+3. Continue with the commit and PR workflow below
 
-## Commit workflow
+## Commit and PR workflow
 
 Commit the changes. Use gh cli to check if a PR exists for this branch. If no PR exists, create one with an appropriate title and description. If a PR exists, query its current title and description and update them if the new changes warrant it. Push the changes.
 
@@ -39,4 +39,22 @@ cat <<'EOF' | gh pr edit <branch-or-number> --body-file -
 EOF
 ```
 
+## CI and review gating
+
+Do not report completion to the user until all required GitHub PR checks pass.
+
+After every push:
+
+1. Watch the PR checks with `gh pr checks --watch`.
+2. Wait for all required checks to complete.
+3. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.
+4. If checks are blocked on AI review bots, wait for bot completion and read all bot reviews before reporting completion.
+
+AI review bot handling:
+
+1. Read every new AI review comment on the PR, including multiple reviews from multiple bots.
+2. Analyze each concern and classify it as valid, partially valid, or not valid.
+3. For valid or partially valid concerns, apply fixes, commit, push, and restart the CI loop.
+4. For concerns that are not valid, explain why with concrete technical reasoning when you report status to the user.
+
 For follow-up edits in this session, continue to commit, push, and update the PR as needed.
PATCH

echo "Gold patch applied."
