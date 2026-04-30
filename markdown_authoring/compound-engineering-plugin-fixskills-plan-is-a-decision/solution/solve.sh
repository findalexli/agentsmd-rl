#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "If a plan is found, read its **Requirements Trace** (R1, R2, etc.) and **Impleme" "plugins/compound-engineering/skills/ce-code-review/SKILL.md" && grep -qF "Each unit's heading carries a stable U-ID prefix matching the format used for R/" "plugins/compound-engineering/skills/ce-plan/SKILL.md" && grep -qF "- **Do not edit the plan body during execution.** The plan is a decision artifac" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "- **Do not edit the plan body during execution.** The plan is a decision artifac" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-code-review/SKILL.md b/plugins/compound-engineering/skills/ce-code-review/SKILL.md
@@ -159,7 +159,7 @@ Every review spawns all 4 always-on personas plus the 2 CE always-on agents, the
 The following paths are compound-engineering pipeline artifacts and must never be flagged for deletion, removal, or gitignore by any reviewer:
 
 - `docs/brainstorms/*` -- requirements documents created by ce-brainstorm
-- `docs/plans/*.md` -- plan files created by ce-plan (living documents with progress checkboxes)
+- `docs/plans/*.md` -- plan files created by ce-plan (decision artifacts; execution progress is derived from git, not stored in plan bodies)
 - `docs/solutions/*.md` -- solution documents created during the pipeline
 
 If a reviewer flags any file in these directories for cleanup or removal, discard that finding during synthesis.
@@ -354,7 +354,7 @@ Locate the plan document so Stage 6 can verify requirements completeness. Check
 - Multiple/ambiguous PR body matches -> `plan_source: inferred` (lower confidence)
 - Auto-discover with single unambiguous match -> `plan_source: inferred` (lower confidence)
 
-If a plan is found, read its **Requirements Trace** (R1, R2, etc.) and **Implementation Units** (checkbox items). Store the extracted requirements list and `plan_source` for Stage 6. Do not block the review if no plan is found — requirements verification is additive, not required.
+If a plan is found, read its **Requirements Trace** (R1, R2, etc.) and **Implementation Units** (items listed under the `## Implementation Units` section). Store the extracted requirements list and `plan_source` for Stage 6. Do not block the review if no plan is found — requirements verification is additive, not required.
 
 ### Stage 3: Select reviewers
 
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -64,7 +64,7 @@ A plan is ready when an implementer can start confidently without needing the pl
 If the user references an existing plan file or there is an obvious recent matching plan in `docs/plans/`:
 - Read it
 - Confirm whether to update it in place or create a new plan
-- If updating, preserve completed checkboxes and revise only the still-relevant sections
+- If updating, revise only the still-relevant sections. Plans do not carry per-unit progress state — progress is derived from git by `ce-work`, so there is no progress to preserve across edits
 
 **Deepen intent:** The word "deepen" (or "deepening") in reference to a plan is the primary trigger for the deepening fast path. When the user says "deepen the plan", "deepen my plan", "run a deepening pass", or similar, the target document is a **plan** in `docs/plans/`, not a requirements document. Use any path, keyword, or context the user provides to identify the right plan. If a path is provided, verify it is actually a plan document. If the match is not obvious, confirm with the user before proceeding.
 
@@ -321,7 +321,6 @@ Good units are:
 - Usually touching a small cluster of related files
 - Ordered by dependency
 - Concrete enough for execution without pre-writing code
-- Marked with checkbox syntax for progress tracking
 
 Avoid:
 - 2-5 minute micro-steps
@@ -373,7 +372,7 @@ The tree is a scope declaration showing the expected output shape. It is not a c
 
 #### 3.5 Define Each Implementation Unit
 
-Each unit's heading carries a stable U-ID prefix matching the format used for R/A/F/AE in requirements docs: `- [ ] U1. **[Name]**`. The prefix is plain text, not bolded — the bold is reserved for the unit name. Number sequentially within the plan starting at U1.
+Each unit's heading carries a stable U-ID prefix matching the format used for R/A/F/AE in requirements docs: `- U1. **[Name]**`. The prefix is plain text, not bolded — the bold is reserved for the unit name. Number sequentially within the plan starting at U1. Do not prefix units with `- [ ]` / `- [x]` checkbox markers; the plan is a decision artifact, and execution progress is derived from git by `ce-work` rather than stored in the plan body.
 
 **Stability rule.** Once assigned, a U-ID is never renumbered. Reordering units leaves their IDs in place (e.g., U1, U3, U5 in their new order is correct; renumbering to U1, U2, U3 is not). Splitting a unit keeps the original U-ID on the original concept and assigns the next unused number to the new unit. Deletion leaves a gap; gaps are fine. This rule matters most during deepening (Phase 5.3), which is the most likely accidental-renumber vector.
 
@@ -603,7 +602,7 @@ deepened: YYYY-MM-DD  # optional, set when the confidence check substantively st
      a gap. This anchor is what ce-work references in blockers and verification, so
      stability across plan edits is load-bearing. -->
 
-- [ ] U1. **[Name]**
+- U1. **[Name]**
 
 **Goal:** [What this unit accomplishes]
 
@@ -723,7 +722,6 @@ For larger `Deep` plans, extend the core template only when useful with sections
 - **Horizontal rules (`---`) between top-level sections** in Standard and Deep plans, mirroring the `ce-brainstorm` requirements doc convention. Improves scannability of dense plans where many H2 sections sit close together. Omit for Lightweight plans where the whole doc fits on a single screen.
 - **All file paths must be repo-relative** — never use absolute paths like `/Users/name/Code/project/src/file.ts`. Use `src/file.ts` instead. Absolute paths make plans non-portable across machines, worktrees, and teammates. When a plan targets a different repo than the document's home, state the target repo once at the top of the plan (e.g., `**Target repo:** my-other-project`) and use repo-relative paths throughout
 - Prefer path plus class/component/pattern references over brittle line numbers
-- Keep implementation units checkable with `- [ ]` syntax for progress tracking
 - Do not include implementation code — no imports, exact method signatures, or framework-specific syntax
 - Pseudo-code sketches and DSL grammars are allowed in the High-Level Technical Design section and per-unit technical design fields when they communicate design direction. Frame them explicitly as directional guidance, not implementation specification
 - Mermaid diagrams are encouraged when they clarify relationships or flows that prose alone would make hard to follow — ERDs for data model changes, sequence diagrams for multi-service interactions, state diagrams for lifecycle transitions, flowcharts for complex branching logic
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -110,6 +110,7 @@ Determine how to proceed based on what was provided in `<input_document>`.
    - If anything is unclear or ambiguous, ask clarifying questions now
    - If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority, not something to renegotiate
    - **Do not skip this** - better to ask questions now than build the wrong thing
+   - **Do not edit the plan body during execution.** The plan is a decision artifact; progress lives in git commits and the task tracker. The only plan mutation during ce-work is the final `status: active → completed` flip at shipping (see `references/shipping-workflow.md` Phase 4 Step 2). Legacy plans may contain `- [ ]` / `- [x]` marks on unit headings — ignore them as state; per-unit completion is determined during execution by reading the current file state.
 
 2. **Setup Environment**
 
@@ -213,15 +214,15 @@ Determine how to proceed based on what was provided in `<input_document>`.
    1. Review the subagent's diff — verify changes match the unit's scope and `Files:` list
    2. Run the relevant test suite to confirm the tree is healthy
    3. If tests fail, diagnose and fix before proceeding — do not dispatch dependent units on a broken tree
-   4. Update the plan checkboxes and task list
+   4. Update the task list (do not edit the plan body — progress is carried by the commit)
    5. Dispatch the next unit
 
    **After all parallel subagents in a batch complete:**
    1. Wait for every subagent in the current parallel batch to finish before acting on any of their results
    2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not anticipated during planning — this is expected, since plans describe *what* not *how*. A collision only matters when 2+ subagents in the same batch modified the same file. In a shared working directory, only the last writer's version survives — the other unit's changes to that file are lost. If a collision is detected: commit all non-colliding files from all units first, then re-run the affected units serially for the shared file so each builds on the other's committed work
    3. For each completed unit, in dependency order: review the diff, run the relevant test suite, stage only that unit's files, and commit with a conventional message derived from the unit's Goal
    4. If tests fail after committing a unit's changes, diagnose and fix before committing the next unit
-   5. Update the plan checkboxes and task list
+   5. Update the task list (do not edit the plan body — progress is carried by the commits just made)
    6. Dispatch the next batch of independent units, or the next dependent unit
 
 ### Phase 2: Execute
@@ -234,6 +235,7 @@ Determine how to proceed based on what was provided in `<input_document>`.
    while (tasks remain):
      - Mark task as in-progress
      - Read any referenced files from the plan or discovered during Phase 0
+     - **If the unit's work is already present and matches the plan's intent** (files exist with the expected capability, or the unit's `Verification` criteria are already satisfied by the current code), the work has likely shipped on a prior branch or session. Verify it matches, mark the task complete, and move on. Do not silently reimplement.
      - Look for similar patterns in codebase
      - Find existing test files for implementation files being changed (Test Discovery — see below)
      - If delegation_active: branch to the Codex Delegation Execution Loop
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -57,6 +57,7 @@ Determine how to proceed based on what was provided in `<input_document>`.
    - If anything is unclear or ambiguous, ask clarifying questions now
    - If clarifying questions were needed above, get user approval on the resolved answers. If no clarifications were needed, proceed without a separate approval step — plan scope is the plan's authority, not something to renegotiate
    - **Do not skip this** - better to ask questions now than build the wrong thing
+   - **Do not edit the plan body during execution.** The plan is a decision artifact; progress lives in git commits and the task tracker. The only plan mutation during ce-work is the final `status: active → completed` flip at shipping (see `references/shipping-workflow.md` Phase 4 Step 2). Legacy plans may contain `- [ ]` / `- [x]` marks on unit headings — ignore them as state; per-unit completion is determined during execution by reading the current file state.
 
 2. **Setup Environment**
 
@@ -158,15 +159,15 @@ Determine how to proceed based on what was provided in `<input_document>`.
    1. Review the subagent's diff — verify changes match the unit's scope and `Files:` list
    2. Run the relevant test suite to confirm the tree is healthy
    3. If tests fail, diagnose and fix before proceeding — do not dispatch dependent units on a broken tree
-   4. Update the plan checkboxes and task list
+   4. Update the task list (do not edit the plan body — progress is carried by the commit)
    5. Dispatch the next unit
 
    **After all parallel subagents in a batch complete:**
    1. Wait for every subagent in the current parallel batch to finish before acting on any of their results
    2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not anticipated during planning — this is expected, since plans describe *what* not *how*. A collision only matters when 2+ subagents in the same batch modified the same file. In a shared working directory, only the last writer's version survives — the other unit's changes to that file are lost. If a collision is detected: commit all non-colliding files from all units first, then re-run the affected units serially for the shared file so each builds on the other's committed work
    3. For each completed unit, in dependency order: review the diff, run the relevant test suite, stage only that unit's files, and commit with a conventional message derived from the unit's Goal
    4. If tests fail after committing a unit's changes, diagnose and fix before committing the next unit
-   5. Update the plan checkboxes and task list
+   5. Update the task list (do not edit the plan body — progress is carried by the commits just made)
    6. Dispatch the next batch of independent units, or the next dependent unit
 
 ### Phase 2: Execute
@@ -179,6 +180,7 @@ Determine how to proceed based on what was provided in `<input_document>`.
    while (tasks remain):
      - Mark task as in-progress
      - Read any referenced files from the plan or discovered during Phase 0
+     - **If the unit's work is already present and matches the plan's intent** (files exist with the expected capability, or the unit's `Verification` criteria are already satisfied by the current code), the work has likely shipped on a prior branch or session. Verify it matches, mark the task complete, and move on. Do not silently reimplement.
      - Look for similar patterns in codebase
      - Find existing test files for implementation files being changed (Test Discovery — see below)
      - Implement following existing conventions
PATCH

echo "Gold patch applied."
