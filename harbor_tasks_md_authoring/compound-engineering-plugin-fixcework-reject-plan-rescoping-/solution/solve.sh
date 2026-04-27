#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- **Re-scoping the plan into human-time phases** - The plan's Implementation Uni" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "- **Re-scoping the plan into human-time phases** - The plan's Implementation Uni" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -108,7 +108,7 @@ Determine how to proceed based on what was provided in `<input_document>`.
    - Review any references or links provided in the plan
    - If the user explicitly asks for TDD, test-first, or characterization-first execution in this session, honor that request even if the plan has no `Execution note`
    - If anything is unclear or ambiguous, ask clarifying questions now
-   - Get user approval to proceed
+   - If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority, not something to renegotiate
    - **Do not skip this** - better to ask questions now than build the wrong thing
 
 2. **Setup Environment**
@@ -414,3 +414,4 @@ When `delegation_active` is true after argument parsing, read `references/codex-
 - **Forgetting to track progress** - Update task status as you go or lose track of what's done
 - **80% done syndrome** - Finish the feature, don't move on early
 - **Skipping review** - Every change gets reviewed; only the depth varies
+- **Re-scoping the plan into human-time phases** - The plan's Implementation Units define the scope of execution. Do not estimate human-hours per unit, propose multi-day breakdowns, or ask the user to pick a subset of units for "this session". Agents execute at agent speed, and context-window pressure is addressed by subagent dispatch (Phase 1 Step 4), not by phased sessions. If a plan-file input is genuinely too large for a single execution, say so plainly and suggest the user return to `/ce-plan` to reduce scope — don't invent session phases as a workaround. For bare-prompt input, Phase 0's Large routing already handles oversized work
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -55,7 +55,7 @@ Determine how to proceed based on what was provided in `<input_document>`.
    - Review any references or links provided in the plan
    - If the user explicitly asks for TDD, test-first, or characterization-first execution in this session, honor that request even if the plan has no `Execution note`
    - If anything is unclear or ambiguous, ask clarifying questions now
-   - Get user approval to proceed
+   - If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority, not something to renegotiate
    - **Do not skip this** - better to ask questions now than build the wrong thing
 
 2. **Setup Environment**
@@ -341,3 +341,4 @@ When all Phase 2 tasks are complete and execution transitions to quality check,
 - **Forgetting to track progress** - Update task status as you go or lose track of what's done
 - **80% done syndrome** - Finish the feature, don't move on early
 - **Skipping review** - Every change gets reviewed; only the depth varies
+- **Re-scoping the plan into human-time phases** - The plan's Implementation Units define the scope of execution. Do not estimate human-hours per unit, propose multi-day breakdowns, or ask the user to pick a subset of units for "this session". Agents execute at agent speed, and context-window pressure is addressed by subagent dispatch (Phase 1 Step 4), not by phased sessions. If a plan-file input is genuinely too large for a single execution, say so plainly and suggest the user return to `/ce-plan` to reduce scope — don't invent session phases as a workaround. For bare-prompt input, Phase 0's Large routing already handles oversized work
PATCH

echo "Gold patch applied."
