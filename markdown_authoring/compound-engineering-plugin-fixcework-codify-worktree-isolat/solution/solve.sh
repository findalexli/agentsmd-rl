#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "3. Merge each subagent's branch into the orchestrator's branch sequentially in d" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "3. Merge each subagent's branch into the orchestrator's branch sequentially in d" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -194,19 +194,25 @@ Determine how to proceed based on what was provided in `<input_document>`.
 
    1. Build a file-to-unit mapping from every candidate unit's `Files:` section (Create, Modify, and Test paths)
    2. Check for intersection — any file path appearing in 2+ units means overlap
-   3. If any overlap is found, downgrade to serial subagents. Log the reason (e.g., "Units 2 and 4 share `config/routes.rb` — using serial dispatch"). Serial subagents still provide context-window isolation without shared-directory risks
+   3. **If overlap is found AND worktree isolation is unavailable**: downgrade to serial subagents. Log the reason (e.g., "Units 2 and 4 share `config/routes.rb` — using serial dispatch"). Serial subagents still provide context-window isolation without shared-directory write races.
+   4. **If overlap is found AND worktree isolation is available**: parallel dispatch is still safe — subagents work in isolation, and the overlap surfaces as a predictable merge conflict the orchestrator handles via the post-batch flow below. Log the predicted overlap so the post-batch flow knows which merges to expect conflicts on.
 
-   Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick up each other's in-progress changes). The parallel subagent constraints below mitigate these.
+   Even with no file overlap, parallel subagents sharing the orchestrator's working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick up each other's in-progress changes). Worktree isolation eliminates both; the shared-directory fallback constraints below mitigate them.
+
+   **Subagent isolation** — give each parallel subagent its own working tree:
+   - **Claude Code (`Agent` tool):** pass `isolation: "worktree"` and `run_in_background: true`. The harness creates a per-subagent worktree under `.claude/worktrees/agent-<id>` on its own branch. Verify `.claude/worktrees/` is gitignored before relying on this.
+   - **Other platforms** without built-in worktree isolation (e.g., Codex `spawn_agent`, Pi `subagent`): subagents share the orchestrator's directory.
 
    **Subagent dispatch** uses your available subagent or task spawning mechanism. For each unit, give the subagent:
    - The full plan file path (for overall context)
    - The specific unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, and Verification
    - Any resolved deferred questions relevant to that unit
    - Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests
 
-   **Parallel subagent constraints** — when dispatching units in parallel (not serial or inline):
+   **Shared-directory fallback constraints** — apply only when worktree isolation is unavailable:
    - Instruct each subagent: "Do not stage files (`git add`), create commits, or run the project test suite. The orchestrator handles testing, staging, and committing after all parallel units complete."
-   - These constraints prevent git index contention and test interference between concurrent subagents
+   - These constraints prevent git index contention and test interference between concurrent subagents.
+   - With worktree isolation active, omit these constraints — subagents may stage, commit, and run their unit's tests within their own worktree branch.
 
    **Permission mode:** Omit the `mode` parameter when dispatching subagents so the user's configured permission settings apply. Do not pass `mode: "auto"` — it overrides user-level settings like `bypassPermissions`.
 
@@ -217,7 +223,19 @@ Determine how to proceed based on what was provided in `<input_document>`.
    4. Update the task list (do not edit the plan body — progress is carried by the commit)
    5. Dispatch the next unit
 
-   **After all parallel subagents in a batch complete:**
+   **After all parallel subagents in a batch complete (worktree-isolated mode):**
+   1. Wait for every subagent in the current parallel batch to finish.
+   2. For each completed subagent, in dependency order: review the worktree's diff against the orchestrator's branch. If the subagent did not commit its own work, stage and commit it inside that worktree.
+   3. Merge each subagent's branch into the orchestrator's branch sequentially in dependency order. **If a merge conflict surfaces, abort the merge (`git merge --abort`) and re-dispatch the conflicting unit serially against the now-merged tree** — hand-resolving silently picks a side and discards one unit's intent. (Predicted overlap from the Parallel Safety Check surfaces here as a conflict, not as silent data loss in shared-directory mode.)
+   4. After each merge, run the relevant test suite. If tests fail, diagnose and fix before merging the next branch.
+   5. Update the task list (progress is carried by the merge commits).
+   6. After merging, remove each subagent's worktree and delete its branch. Use the absolute path and branch name returned in the subagent's result.
+      - Unlock the worktree first — the harness locks per-subagent worktrees: `git worktree unlock <absolute-path>`
+      - Remove the worktree: `git worktree remove <absolute-path>`
+      - Delete the branch: `git branch -d <branch-name>` (the branch outlives the worktree by default and accumulates as orphans if not cleaned up; `-d` lowercase refuses to delete unmerged branches, which is the safety we want — if it fails, investigate before forcing)
+   7. Dispatch the next batch of independent units, or the next dependent unit.
+
+   **After all parallel subagents in a batch complete (shared-directory fallback):**
    1. Wait for every subagent in the current parallel batch to finish before acting on any of their results
    2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not anticipated during planning — this is expected, since plans describe *what* not *how*. A collision only matters when 2+ subagents in the same batch modified the same file. In a shared working directory, only the last writer's version survives — the other unit's changes to that file are lost. If a collision is detected: commit all non-colliding files from all units first, then re-run the affected units serially for the shared file so each builds on the other's committed work
    3. For each completed unit, in dependency order: review the diff, run the relevant test suite, stage only that unit's files, and commit with a conventional message derived from the unit's Goal
@@ -314,7 +332,9 @@ Determine how to proceed based on what was provided in `<input_document>`.
 
    **Note:** Incremental commits use clean conventional messages without attribution footers. The final Phase 4 commit/PR includes the full attribution.
 
-   **Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel subagent constraints in Phase 1 Step 4). The commit guidance in this section applies to inline and serial execution, and to the orchestrator's commit decisions after parallel batch completion.
+   **Parallel subagent mode:** Commit ownership is split by isolation mode (see Phase 1 Step 4):
+   - **Worktree-isolated:** subagents may stage and commit inside their own worktree branch; the orchestrator merges those branches in dependency order after the batch.
+   - **Shared-directory fallback:** subagents do not commit; the orchestrator stages and commits each unit after the entire parallel batch completes.
 
 3. **Follow Existing Patterns**
 
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -139,19 +139,25 @@ Determine how to proceed based on what was provided in `<input_document>`.
 
    1. Build a file-to-unit mapping from every candidate unit's `Files:` section (Create, Modify, and Test paths)
    2. Check for intersection — any file path appearing in 2+ units means overlap
-   3. If any overlap is found, downgrade to serial subagents. Log the reason (e.g., "Units 2 and 4 share `config/routes.rb` — using serial dispatch"). Serial subagents still provide context-window isolation without shared-directory risks
+   3. **If overlap is found AND worktree isolation is unavailable**: downgrade to serial subagents. Log the reason (e.g., "Units 2 and 4 share `config/routes.rb` — using serial dispatch"). Serial subagents still provide context-window isolation without shared-directory write races.
+   4. **If overlap is found AND worktree isolation is available**: parallel dispatch is still safe — subagents work in isolation, and the overlap surfaces as a predictable merge conflict the orchestrator handles via the post-batch flow below. Log the predicted overlap so the post-batch flow knows which merges to expect conflicts on.
 
-   Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick up each other's in-progress changes). The parallel subagent constraints below mitigate these.
+   Even with no file overlap, parallel subagents sharing the orchestrator's working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick up each other's in-progress changes). Worktree isolation eliminates both; the shared-directory fallback constraints below mitigate them.
+
+   **Subagent isolation** — give each parallel subagent its own working tree:
+   - **Claude Code (`Agent` tool):** pass `isolation: "worktree"` and `run_in_background: true`. The harness creates a per-subagent worktree under `.claude/worktrees/agent-<id>` on its own branch. Verify `.claude/worktrees/` is gitignored before relying on this.
+   - **Other platforms** without built-in worktree isolation (e.g., Codex `spawn_agent`, Pi `subagent`): subagents share the orchestrator's directory.
 
    **Subagent dispatch** uses your available subagent or task spawning mechanism. For each unit, give the subagent:
    - The full plan file path (for overall context)
    - The specific unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, and Verification
    - Any resolved deferred questions relevant to that unit
    - Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests
 
-   **Parallel subagent constraints** — when dispatching units in parallel (not serial or inline):
+   **Shared-directory fallback constraints** — apply only when worktree isolation is unavailable:
    - Instruct each subagent: "Do not stage files (`git add`), create commits, or run the project test suite. The orchestrator handles testing, staging, and committing after all parallel units complete."
-   - These constraints prevent git index contention and test interference between concurrent subagents
+   - These constraints prevent git index contention and test interference between concurrent subagents.
+   - With worktree isolation active, omit these constraints — subagents may stage, commit, and run their unit's tests within their own worktree branch.
 
    **Permission mode:** Omit the `mode` parameter when dispatching subagents so the user's configured permission settings apply. Do not pass `mode: "auto"` — it overrides user-level settings like `bypassPermissions`.
 
@@ -162,7 +168,19 @@ Determine how to proceed based on what was provided in `<input_document>`.
    4. Update the task list (do not edit the plan body — progress is carried by the commit)
    5. Dispatch the next unit
 
-   **After all parallel subagents in a batch complete:**
+   **After all parallel subagents in a batch complete (worktree-isolated mode):**
+   1. Wait for every subagent in the current parallel batch to finish.
+   2. For each completed subagent, in dependency order: review the worktree's diff against the orchestrator's branch. If the subagent did not commit its own work, stage and commit it inside that worktree.
+   3. Merge each subagent's branch into the orchestrator's branch sequentially in dependency order. **If a merge conflict surfaces, abort the merge (`git merge --abort`) and re-dispatch the conflicting unit serially against the now-merged tree** — hand-resolving silently picks a side and discards one unit's intent. (Predicted overlap from the Parallel Safety Check surfaces here as a conflict, not as silent data loss in shared-directory mode.)
+   4. After each merge, run the relevant test suite. If tests fail, diagnose and fix before merging the next branch.
+   5. Update the task list (progress is carried by the merge commits).
+   6. After merging, remove each subagent's worktree and delete its branch. Use the absolute path and branch name returned in the subagent's result.
+      - Unlock the worktree first — the harness locks per-subagent worktrees: `git worktree unlock <absolute-path>`
+      - Remove the worktree: `git worktree remove <absolute-path>`
+      - Delete the branch: `git branch -d <branch-name>` (the branch outlives the worktree by default and accumulates as orphans if not cleaned up; `-d` lowercase refuses to delete unmerged branches, which is the safety we want — if it fails, investigate before forcing)
+   7. Dispatch the next batch of independent units, or the next dependent unit.
+
+   **After all parallel subagents in a batch complete (shared-directory fallback):**
    1. Wait for every subagent in the current parallel batch to finish before acting on any of their results
    2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not anticipated during planning — this is expected, since plans describe *what* not *how*. A collision only matters when 2+ subagents in the same batch modified the same file. In a shared working directory, only the last writer's version survives — the other unit's changes to that file are lost. If a collision is detected: commit all non-colliding files from all units first, then re-run the affected units serially for the shared file so each builds on the other's committed work
    3. For each completed unit, in dependency order: review the diff, run the relevant test suite, stage only that unit's files, and commit with a conventional message derived from the unit's Goal
@@ -257,7 +275,9 @@ Determine how to proceed based on what was provided in `<input_document>`.
 
    **Note:** Incremental commits use clean conventional messages without attribution footers. The final Phase 4 commit/PR includes the full attribution.
 
-   **Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel subagent constraints in Phase 1 Step 4). The commit guidance in this section applies to inline and serial execution, and to the orchestrator's commit decisions after parallel batch completion.
+   **Parallel subagent mode:** Commit ownership is split by isolation mode (see Phase 1 Step 4):
+   - **Worktree-isolated:** subagents may stage and commit inside their own worktree branch; the orchestrator merges those branches in dependency order after the batch.
+   - **Shared-directory fallback:** subagents do not commit; the orchestrator stages and commits each unit after the entire parallel batch completes.
 
 3. **Follow Existing Patterns**
 
PATCH

echo "Gold patch applied."
