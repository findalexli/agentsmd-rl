#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

TARGET=".claude/skills/running-tend/SKILL.md"

# Idempotency: skip if the gold section is already in place
if grep -q "Close bot-opened issues once the underlying cause is resolved" "$TARGET"; then
    echo "SKILL.md already contains the issue-management guidance; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/running-tend/SKILL.md b/.claude/skills/running-tend/SKILL.md
--- a/.claude/skills/running-tend/SKILL.md
+++ b/.claude/skills/running-tend/SKILL.md
@@ -16,3 +16,12 @@ error conventions, etc. are in `CLAUDE.md` — don't duplicate them here.
 - Dependency management: Dependabot (tend-weekly is disabled)
 - Automerge: `pull-request-target.yaml` auto-merges single-commit `prql-bot` PRs
   once CI passes
+
+## Issue management
+
+- Close bot-opened issues once the underlying cause is resolved — don't leave
+  them open for a maintainer. If you (prql-bot) filed an issue (e.g., a nightly
+  "tests failed" issue, a code-quality issue, an infra/upstream bug report) and
+  the fix has merged or the upstream problem has been addressed, close the issue
+  with a short comment citing the resolution (e.g., "Resolved by #NNNN —
+  closing"). Applies to any issue where `author.login == prql-bot`.
PATCH

echo "Applied issue-management section to $TARGET"
