#!/usr/bin/env bash
set -euo pipefail

cd /workspace/oh-my-claudecode

# Idempotency guard
if grep -qF "- **Skill vs agent invocation**: `ai-slop-cleaner` is a skill, invoke via `Skill" "skills/ralph/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ralph/SKILL.md b/skills/ralph/SKILL.md
@@ -102,9 +102,11 @@ By default, ralph operates in PRD mode. A scaffold `prd.json` is auto-generated
      4. The list of files changed during the ralph session for context
    - Ralph floor: always at least STANDARD, even for small changes
    - The selected reviewer verifies against the SPECIFIC acceptance criteria from prd.json, not vague "is it done?"
+   - **On APPROVAL: immediately proceed to Step 7.5 in the same turn. Do NOT pause to report the verdict to the user — reporting happens only at Step 8 (`/oh-my-claudecode:cancel`) or on rejection (Step 9). Treating an approved verdict as a reporting checkpoint is a polite-stop anti-pattern.**
 
-7.5 **Mandatory Deslop Pass**:
-   - Unless `{{PROMPT}}` contains `--no-deslop`, run `oh-my-claudecode:ai-slop-cleaner` in standard mode (not `--review`) on the files changed during the current Ralph session only.
+7.5 **Mandatory Deslop Pass** (runs unconditionally after Step 7 approval, unless `{{PROMPT}}` contains `--no-deslop`):
+   - **Invoke the `ai-slop-cleaner` skill via the Skill tool: `Skill("ai-slop-cleaner")`.** Run in standard mode (not `--review`) on the files changed during the current Ralph session only.
+   - **ai-slop-cleaner is a SKILL, not an agent.** Do NOT call it via `Task(subagent_type="oh-my-claudecode:ai-slop-cleaner")` — that subagent type does not exist and the call will fail with "Agent type not found". If you see that error, retry with the Skill tool — do NOT substitute a similarly-named agent like `code-simplifier` as a "closest match".
    - Keep the scope bounded to the Ralph changed-file set; do not broaden the cleanup pass to unrelated files.
    - If the reviewer approved the implementation but the deslop pass introduces follow-up edits, keep those edits inside the same changed-file scope before proceeding.
 
@@ -126,6 +128,7 @@ By default, ralph operates in PRD mode. A scaffold `prd.json` is auto-generated
 - Skip architect consultation for simple feature additions, well-tested changes, or time-critical verification
 - Proceed with architect agent verification alone -- never block on unavailable tools
 - Use `state_write` / `state_read` for ralph mode state persistence between iterations
+- **Skill vs agent invocation**: `ai-slop-cleaner` is a skill, invoke via `Skill("ai-slop-cleaner")`. `architect`, `critic`, `executor` etc. are agents, invoke via `Task(subagent_type="oh-my-claudecode:<name>")`. If you ever get "Agent type ... not found" for an `oh-my-claudecode:<name>` identifier, the item is a skill — retry with the Skill tool. Do NOT substitute a similarly-named agent as a "closest match".
 </Tool_Usage>
 
 <Examples>
@@ -198,6 +201,7 @@ Why bad: Did not refine scaffold criteria into task-specific ones. This is PRD t
 - Continue working when the hook system sends "The boulder never stops" -- this means the iteration continues
 - If the selected reviewer rejects verification, fix the issues and re-verify (do not stop)
 - If the same issue recurs across 3+ iterations, report it as a potential fundamental problem
+- **Do NOT stop after Step 7 approval.** The boulder continues through 7 → 7.5 → 7.6 → 8 in the same turn as a single chain. Step 7 is a checkpoint inside the loop, not a reporting moment. Treating an architect/critic APPROVED verdict as "time to summarise and wait for user acknowledgment" is a polite-stop anti-pattern — the only reporting moments in Ralph are Step 8 (successful cancel) or Step 9 (rejection).
 </Escalation_And_Stop_Conditions>
 
 <Final_Checklist>
PATCH

echo "Gold patch applied."
