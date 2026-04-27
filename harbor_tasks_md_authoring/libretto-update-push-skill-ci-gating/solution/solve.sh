#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "For follow-up edits in this session, continue to commit, push, and update the PR" ".agents/skills/push/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/push/SKILL.md b/.agents/skills/push/SKILL.md
@@ -46,10 +46,15 @@ Do not report completion to the user until all required GitHub PR checks pass.
 After every push:
 
 1. Watch PR checks with `gh pr checks --watch`.
-2. If GitHub returns `no checks reported`, treat it as possible propagation delay. Wait 15 seconds and retry `gh pr checks --watch`. Repeat up to 8 times (about 2 minutes total) before concluding there are no checks configured.
-3. Once checks appear, wait for all required checks to complete.
-4. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.
-5. If checks are blocked on AI review bots, wait for bot completion and read all bot reviews before reporting completion.
+2. If GitHub returns `no checks reported`, treat it as possible propagation delay. Wait 15 seconds and retry `gh pr checks --watch`. Repeat up to 8 times (about 2 minutes total).
+3. If checks are still not reported after those retries, run one remediation pass and treat merge conflicts with `main` as a likely cause:
+   - Pull and merge `main` into your branch.
+   - If merge conflicts occur, resolve them by following the `fix-merge-conflicts` skill.
+   - Commit the conflict resolution if needed, push, and restart this CI loop once.
+4. If checks are still not reported after that remediation pass, conclude no required checks are configured for this PR.
+5. If checks appear, wait for all required checks to complete.
+6. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.
+7. If checks are blocked on AI review bots, wait for bot completion and read all bot reviews before reporting completion.
 
 AI review bot handling:
 
@@ -58,4 +63,4 @@ AI review bot handling:
 3. For valid or partially valid concerns, apply fixes, commit, push, and restart the CI loop.
 4. For concerns that are not valid, explain why with concrete technical reasoning when you report status to the user.
 
-For follow-up edits in this session, continue to commit, push, and update the PR as needed.
+For follow-up edits in this session, continue to commit, push, and update the PR as needed. After each follow-up push, re-run the full check-wait loop above (`gh pr checks --watch` and retries) before reporting completion.
PATCH

echo "Gold patch applied."
