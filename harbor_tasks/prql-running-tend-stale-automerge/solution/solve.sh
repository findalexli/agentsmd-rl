#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

SKILL=.claude/skills/running-tend/SKILL.md

# Idempotent: if patch already applied, exit silently.
if grep -q "Automerge: not configured" "$SKILL"; then
    echo "[solve] patch already applied, skipping"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/running-tend/SKILL.md b/.claude/skills/running-tend/SKILL.md
--- a/.claude/skills/running-tend/SKILL.md
+++ b/.claude/skills/running-tend/SKILL.md
@@ -14,8 +14,10 @@ error conventions, etc. are in `CLAUDE.md` — don't duplicate them here.

 - Main CI workflow: `tests` (watched by tend-ci-fix)
 - Dependency management: Dependabot (tend-weekly is disabled)
-- Automerge: `pull-request-target.yaml` auto-merges single-commit `prql-bot` PRs
-  once CI passes
+- Automerge: not configured — `pull-request-target.yaml` only validates PR
+  titles and handles `pr-backport-web` backports. The automerge job was removed
+  in #5753, so bot PRs must be merged manually by a maintainer (or via repo
+  branch-protection auto-merge if a maintainer enables it on the PR).

 ## Issue management

PATCH

echo "[solve] gold patch applied"
