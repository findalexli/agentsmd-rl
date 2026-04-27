#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "2. Cross-check for discovered file collisions: compare the actual files modified" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "2. Cross-check for discovered file collisions: compare the actual files modified" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -186,17 +186,42 @@ Determine how to proceed based on what was provided in `<input_document>`.
    |----------|-------------|
    | **Inline** | 1-2 small tasks, or tasks needing user interaction mid-flight. **Default for bare-prompt work** — bare prompts rarely produce enough structured context to justify subagent dispatch |
    | **Serial subagents** | 3+ tasks with dependencies between them. Each subagent gets a fresh context window focused on one unit — prevents context degradation across many tasks. Requires plan-unit metadata (Goal, Files, Approach, Test scenarios) |
-   | **Parallel subagents** | 3+ tasks where some units have no shared dependencies and touch non-overlapping files. Dispatch independent units simultaneously, run dependent units after their prerequisites complete. Requires plan-unit metadata |
+   | **Parallel subagents** | 3+ tasks that pass the Parallel Safety Check (below). Dispatch independent units simultaneously, run dependent units after their prerequisites complete. Requires plan-unit metadata |
+
+   **Parallel Safety Check** — required before choosing parallel dispatch:
+
+   1. Build a file-to-unit mapping from every candidate unit's `Files:` section (Create, Modify, and Test paths)
+   2. Check for intersection — any file path appearing in 2+ units means overlap
+   3. If any overlap is found, downgrade to serial subagents. Log the reason (e.g., "Units 2 and 4 share `config/routes.rb` — using serial dispatch"). Serial subagents still provide context-window isolation without shared-directory risks
+
+   Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick up each other's in-progress changes). The parallel subagent constraints below mitigate these.
 
    **Subagent dispatch** uses your available subagent or task spawning mechanism. For each unit, give the subagent:
    - The full plan file path (for overall context)
    - The specific unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, and Verification
    - Any resolved deferred questions relevant to that unit
    - Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests
 
+   **Parallel subagent constraints** — when dispatching units in parallel (not serial or inline):
+   - Instruct each subagent: "Do not stage files (`git add`), create commits, or run the project test suite. The orchestrator handles testing, staging, and committing after all parallel units complete."
+   - These constraints prevent git index contention and test interference between concurrent subagents
+
    **Permission mode:** Omit the `mode` parameter when dispatching subagents so the user's configured permission settings apply. Do not pass `mode: "auto"` — it overrides user-level settings like `bypassPermissions`.
 
-   After each subagent completes, update the plan checkboxes and task list before dispatching the next dependent unit.
+   **After each subagent completes (serial mode):**
+   1. Review the subagent's diff — verify changes match the unit's scope and `Files:` list
+   2. Run the relevant test suite to confirm the tree is healthy
+   3. If tests fail, diagnose and fix before proceeding — do not dispatch dependent units on a broken tree
+   4. Update the plan checkboxes and task list
+   5. Dispatch the next unit
+
+   **After all parallel subagents in a batch complete:**
+   1. Wait for every subagent in the current parallel batch to finish before acting on any of their results
+   2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not anticipated during planning — this is expected, since plans describe *what* not *how*. A collision only matters when 2+ subagents in the same batch modified the same file. In a shared working directory, only the last writer's version survives — the other unit's changes to that file are lost. If a collision is detected: commit all non-colliding files from all units first, then re-run the affected units serially for the shared file so each builds on the other's committed work
+   3. For each completed unit, in dependency order: review the diff, run the relevant test suite, stage only that unit's files, and commit with a conventional message derived from the unit's Goal
+   4. If tests fail after committing a unit's changes, diagnose and fix before committing the next unit
+   5. Update the plan checkboxes and task list
+   6. Dispatch the next batch of independent units, or the next dependent unit
 
 ### Phase 2: Execute
 
@@ -286,6 +311,8 @@ Determine how to proceed based on what was provided in `<input_document>`.
 
    **Note:** Incremental commits use clean conventional messages without attribution footers. The final Phase 4 commit/PR includes the full attribution.
 
+   **Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel subagent constraints in Phase 1 Step 4). The commit guidance in this section applies to inline and serial execution, and to the orchestrator's commit decisions after parallel batch completion.
+
 3. **Follow Existing Patterns**
 
    - The plan should reference similar code - read those files first
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -131,17 +131,42 @@ Determine how to proceed based on what was provided in `<input_document>`.
    |----------|-------------|
    | **Inline** | 1-2 small tasks, or tasks needing user interaction mid-flight. **Default for bare-prompt work** — bare prompts rarely produce enough structured context to justify subagent dispatch |
    | **Serial subagents** | 3+ tasks with dependencies between them. Each subagent gets a fresh context window focused on one unit — prevents context degradation across many tasks. Requires plan-unit metadata (Goal, Files, Approach, Test scenarios) |
-   | **Parallel subagents** | 3+ tasks where some units have no shared dependencies and touch non-overlapping files. Dispatch independent units simultaneously, run dependent units after their prerequisites complete. Requires plan-unit metadata |
+   | **Parallel subagents** | 3+ tasks that pass the Parallel Safety Check (below). Dispatch independent units simultaneously, run dependent units after their prerequisites complete. Requires plan-unit metadata |
+
+   **Parallel Safety Check** — required before choosing parallel dispatch:
+
+   1. Build a file-to-unit mapping from every candidate unit's `Files:` section (Create, Modify, and Test paths)
+   2. Check for intersection — any file path appearing in 2+ units means overlap
+   3. If any overlap is found, downgrade to serial subagents. Log the reason (e.g., "Units 2 and 4 share `config/routes.rb` — using serial dispatch"). Serial subagents still provide context-window isolation without shared-directory risks
+
+   Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick up each other's in-progress changes). The parallel subagent constraints below mitigate these.
 
    **Subagent dispatch** uses your available subagent or task spawning mechanism. For each unit, give the subagent:
    - The full plan file path (for overall context)
    - The specific unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, and Verification
    - Any resolved deferred questions relevant to that unit
    - Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests
 
+   **Parallel subagent constraints** — when dispatching units in parallel (not serial or inline):
+   - Instruct each subagent: "Do not stage files (`git add`), create commits, or run the project test suite. The orchestrator handles testing, staging, and committing after all parallel units complete."
+   - These constraints prevent git index contention and test interference between concurrent subagents
+
    **Permission mode:** Omit the `mode` parameter when dispatching subagents so the user's configured permission settings apply. Do not pass `mode: "auto"` — it overrides user-level settings like `bypassPermissions`.
 
-   After each subagent completes, update the plan checkboxes and task list before dispatching the next dependent unit.
+   **After each subagent completes (serial mode):**
+   1. Review the subagent's diff — verify changes match the unit's scope and `Files:` list
+   2. Run the relevant test suite to confirm the tree is healthy
+   3. If tests fail, diagnose and fix before proceeding — do not dispatch dependent units on a broken tree
+   4. Update the plan checkboxes and task list
+   5. Dispatch the next unit
+
+   **After all parallel subagents in a batch complete:**
+   1. Wait for every subagent in the current parallel batch to finish before acting on any of their results
+   2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not anticipated during planning — this is expected, since plans describe *what* not *how*. A collision only matters when 2+ subagents in the same batch modified the same file. In a shared working directory, only the last writer's version survives — the other unit's changes to that file are lost. If a collision is detected: commit all non-colliding files from all units first, then re-run the affected units serially for the shared file so each builds on the other's committed work
+   3. For each completed unit, in dependency order: review the diff, run the relevant test suite, stage only that unit's files, and commit with a conventional message derived from the unit's Goal
+   4. If tests fail after committing a unit's changes, diagnose and fix before committing the next unit
+   5. Update the plan checkboxes and task list
+   6. Dispatch the next batch of independent units, or the next dependent unit
 
 ### Phase 2: Execute
 
@@ -229,6 +254,8 @@ Determine how to proceed based on what was provided in `<input_document>`.
 
    **Note:** Incremental commits use clean conventional messages without attribution footers. The final Phase 4 commit/PR includes the full attribution.
 
+   **Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel subagent constraints in Phase 1 Step 4). The commit guidance in this section applies to inline and serial execution, and to the orchestrator's commit decisions after parallel batch completion.
+
 3. **Follow Existing Patterns**
 
    - The plan should reference similar code - read those files first
PATCH

echo "Gold patch applied."
