#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aidevops

# Idempotency guard
if grep -qF "Hard rules: see \"Framework Rules > Git Workflow > Pre-edit rules\" below. Details" ".agents/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/AGENTS.md b/.agents/AGENTS.md
@@ -43,7 +43,7 @@ New to aidevops? Type `/onboarding`.
 
 > **Skip this section if you don't have Edit/Write/Bash tools** (e.g., Plan+ agent). Instead, proceed directly to responding to the user.
 
-Hard rules: see "Framework Rules > Git Workflow > Pre-edit rules" below. Details: `workflows/pre-edit.md`.
+Hard rules: see "Framework Rules > Git Workflow > Pre-edit rules" below. Details: `.agents/workflows/pre-edit.md`.
 
 Subagent write restrictions: on `main`/`master`, **headless subagents** may write to `README.md`, `TODO.md`, `todo/PLANS.md`, `todo/tasks/*`. **Interactive subagents** must always use a linked worktree regardless of path — no planning exception (t1990). All other writes → proposed edits in a worktree.
 
@@ -344,7 +344,7 @@ Log security ops: `audit-log-helper.sh log <type> <message>`. NEVER log credenti
 
 ### Git Workflow
 
-Git is the audit trail. Procedures: see "Git Workflow" section below.
+Git is the audit trail. Procedures: see the "## Git Workflow" section below.
 
 **Origin labelling (MANDATORY):**
 
PATCH

echo "Gold patch applied."
