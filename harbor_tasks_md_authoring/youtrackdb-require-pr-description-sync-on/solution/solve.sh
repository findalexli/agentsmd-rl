#!/usr/bin/env bash
set -euo pipefail

cd /workspace/youtrackdb

# Idempotency guard
if grep -qF "- **Keep the PR title and description in sync with follow-up commits.** The squa" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -176,6 +176,7 @@ Tests configure YouTrackDB-specific system properties in `<argLine>`:
 - Target branch: `develop`
 - **1 PR = 1 squashed commit** — all branch commits are squashed on merge
 - **Must use the PR template** at `.github/pull_request_template.md`. Every PR must include the Motivation section explaining WHY the change was made.
+- **Keep the PR title and description in sync with follow-up commits.** The squashed commit message is built from the PR title and description, not from individual commit messages — update them with every push so the merge commit reflects all changes.
 - **Test count gate bypass**: Add `[no-test-number-check]` to the PR title to skip the test count gate. Use this only for intentional test refactorings that restructure or consolidate tests without reducing coverage.
 
 ### Workflow Artifacts
PATCH

echo "Gold patch applied."
