#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openhands-infra

# Idempotency guard
if grep -qF "**Common violation**: Skipping skill invocation and jumping straight to coding. " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,18 +2,48 @@
 
 ## Development Workflow (MANDATORY)
 
-**CRITICAL**: All feature development and bug fixes MUST strictly follow the `github-workflow` skill.
+**CRITICAL**: All feature development, bug fixes, and dependency updates MUST strictly follow the `github-workflow` skill.
 
-Before ANY code changes involving functionality:
-1. **Invoke skill**: Use `/github-workflow` or load the skill
-2. **Follow the 10-step workflow** - NO shortcuts allowed
+### Rule 1: ALWAYS Invoke the Skill First
+
+Before ANY code changes — features, fixes, refactors, dependency bumps — you MUST:
+1. **Invoke skill**: Use `/github-workflow` or read `.claude/skills/github-workflow/SKILL.md`
+2. **Follow ALL 10 steps** in order — NO shortcuts, NO skipping steps
 3. **Do NOT merge** - Report status and wait for user decision
 
-The workflow includes:
-- Step 2: Write new unit tests + update E2E test cases
-- Steps 6-7: Address ALL reviewer bot findings (Q, Codex, etc.) and iterate until no new findings
-- Steps 8-9: Deploy to staging + run full E2E tests
-- Step 10: Report ready status (DO NOT MERGE)
+**Common violation**: Skipping skill invocation and jumping straight to coding. This causes missed steps (reviewer bot iteration, PR templates, E2E test selection). The skill is not optional guidance — it is the required process.
+
+### Rule 2: ALWAYS Use Git Worktrees for Code Changes
+
+**Every** branch that changes code MUST use a worktree for isolation:
+```bash
+git fetch origin main
+git worktree add .worktrees/<name> -b <type>/<name> origin/main
+cd .worktrees/<name>
+npm install   # worktrees don't share node_modules
+# ... do all work here ...
+```
+
+After merge, clean up:
+```bash
+git worktree remove .worktrees/<name>
+git branch -d <type>/<name>
+```
+
+**Common violation**: Using `git checkout -b` on the main working tree. This pollutes the workspace and risks uncommitted changes interfering with the feature branch.
+
+**Only exception**: Trivial docs-only changes (README typos) with zero code impact.
+
+### Rule 3: Complete ALL Workflow Steps
+
+The 10-step workflow is not a suggestion — every step must be completed:
+- Step 1: Create **worktree** + branch (not `git checkout -b`)
+- Step 2: Implement + write/update tests
+- Step 3: Build + test locally
+- Step 4: Commit + create PR with checklist template
+- Steps 5-7: CI checks + address ALL reviewer bot findings + iterate until clean
+- Steps 8-9: Deploy to staging + run E2E tests (use `test/select-e2e-tests.sh`)
+- Step 10: Report ready status (DO NOT MERGE unless user explicitly says to)
 
 ## Quick Reference
 
PATCH

echo "Gold patch applied."
