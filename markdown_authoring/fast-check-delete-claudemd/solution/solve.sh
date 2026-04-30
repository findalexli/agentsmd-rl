#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fast-check

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,9 +0,0 @@
-# Claude guidance for fast-check
-
-## Pull requests
-
-When opening or updating a pull request in this repo, follow the
-`pr-authoring` skill at `.claude/skills/pr-authoring/SKILL.md`.
-It covers the PR template, the gitmoji title format, the required
-description structure, and the rule that checkboxes stay unchecked
-(reviewers tick them, not the author).
PATCH

echo "Gold patch applied."
