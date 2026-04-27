#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "**Test Discovery** \u2014 Before implementing changes to a file, find its existing te" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "**Test Discovery** \u2014 Before implementing changes to a file, find its existing te" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -1,27 +1,51 @@
 ---
 name: ce:work-beta
-description: "[BETA] Execute work plans with external delegate support. Same as ce:work but includes experimental Codex delegation mode for token-conserving code implementation."
-argument-hint: "[plan file, specification, or todo file path]"
+description: "[BETA] Execute work with external delegate support. Same as ce:work but includes experimental Codex delegation mode for token-conserving code implementation."
+argument-hint: "[plan file path or description of work to do]"
 disable-model-invocation: true
 ---
 
-# Work Plan Execution Command
+# Work Execution Command
 
-Execute a work plan efficiently while maintaining quality and finishing features.
+Execute work efficiently while maintaining quality and finishing features.
 
 ## Introduction
 
-This command takes a work document (plan, specification, or todo file) and executes it systematically. The focus is on **shipping complete features** by understanding requirements quickly, following existing patterns, and maintaining quality throughout.
+This command takes a work document (plan, specification, or todo file) or a bare prompt describing the work, and executes it systematically. The focus is on **shipping complete features** by understanding requirements quickly, following existing patterns, and maintaining quality throughout.
 
 ## Input Document
 
 <input_document> #$ARGUMENTS </input_document>
 
 ## Execution Workflow
 
+### Phase 0: Input Triage
+
+Determine how to proceed based on what was provided in `<input_document>`.
+
+**Plan document** (input is a file path to an existing plan, specification, or todo file) → skip to Phase 1.
+
+**Bare prompt** (input is a description of work, not a file path):
+
+1. **Scan the work area**
+
+   - Identify files likely to change based on the prompt
+   - Find existing test files for those areas (search for test/spec files that import, reference, or share names with the implementation files)
+   - Note local patterns and conventions in the affected areas
+
+2. **Assess complexity and route**
+
+   | Complexity | Signals | Action |
+   |-----------|---------|--------|
+   | **Trivial** | 1-2 files, no behavioral change (typo, config, rename) | Proceed to Phase 1 step 2 (environment setup), then implement directly — no task list, no execution loop. Apply Test Discovery if the change touches behavior-bearing code |
+   | **Small / Medium** | Clear scope, under ~10 files | Build a task list from discovery. Proceed to Phase 1 step 2 |
+   | **Large** | Cross-cutting, architectural decisions, 10+ files, touches auth/payments/migrations | Inform the user this would benefit from `/ce:brainstorm` or `/ce:plan` to surface edge cases and scope boundaries. Honor their choice. If proceeding, build a task list and continue to Phase 1 step 2 |
+
+---
+
 ### Phase 1: Quick Start
 
-1. **Read Plan and Clarify**
+1. **Read Plan and Clarify** _(skip if arriving from Phase 0 with a bare prompt)_
 
    - Read the work document completely
    - Treat the plan as a decision artifact, not an execution script
@@ -79,7 +103,7 @@ This command takes a work document (plan, specification, or todo file) and execu
    - You want to keep the default branch clean while experimenting
    - You plan to switch between branches frequently
 
-3. **Create Todo List**
+3. **Create Todo List** _(skip if Phase 0 already built one, or if Phase 0 routed as Trivial)_
    - Use your available task tracking tool (e.g., TodoWrite, task lists) to break the plan into actionable tasks
    - Derive tasks from the plan's implementation units, dependencies, files, test targets, and verification criteria
    - Carry each unit's `Execution note` into the task when present
@@ -97,9 +121,9 @@ This command takes a work document (plan, specification, or todo file) and execu
 
    | Strategy | When to use |
    |----------|-------------|
-   | **Inline** | 1-2 small tasks, or tasks needing user interaction mid-flight |
-   | **Serial subagents** | 3+ tasks with dependencies between them. Each subagent gets a fresh context window focused on one unit — prevents context degradation across many tasks |
-   | **Parallel subagents** | 3+ tasks where some units have no shared dependencies and touch non-overlapping files. Dispatch independent units simultaneously, run dependent units after their prerequisites complete |
+   | **Inline** | 1-2 small tasks, or tasks needing user interaction mid-flight. **Default for bare-prompt work** — bare prompts rarely produce enough structured context to justify subagent dispatch |
+   | **Serial subagents** | 3+ tasks with dependencies between them. Each subagent gets a fresh context window focused on one unit — prevents context degradation across many tasks. Requires plan-unit metadata (Goal, Files, Approach, Test scenarios) |
+   | **Parallel subagents** | 3+ tasks where some units have no shared dependencies and touch non-overlapping files. Dispatch independent units simultaneously, run dependent units after their prerequisites complete. Requires plan-unit metadata |
 
    **Subagent dispatch** uses your available subagent or task spawning mechanism. For each unit, give the subagent:
    - The full plan file path (for overall context)
@@ -120,10 +144,11 @@ This command takes a work document (plan, specification, or todo file) and execu
    ```
    while (tasks remain):
      - Mark task as in-progress
-     - Read any referenced files from the plan
+     - Read any referenced files from the plan or discovered during Phase 0
      - Look for similar patterns in codebase
+     - Find existing test files for implementation files being changed (Test Discovery — see below)
      - Implement following existing conventions
-     - Write tests for new functionality
+     - Add, update, or remove tests to match implementation changes (see Test Discovery below)
      - Run System-Wide Test Check (see below)
      - Run tests after changes
      - Mark task as completed
@@ -138,6 +163,8 @@ This command takes a work document (plan, specification, or todo file) and execu
    - Do not over-implement beyond the current behavior slice when working test-first
    - Skip test-first discipline for trivial renames, pure configuration, and pure styling work
 
+   **Test Discovery** — Before implementing changes to a file, find its existing test files (search for test/spec files that import, reference, or share naming patterns with the implementation file). When a plan specifies test scenarios or test files, start there, then check for additional test coverage the plan may not have enumerated. Changes to implementation files should be accompanied by corresponding test updates — new tests for new behavior, modified tests for changed behavior, removed or updated tests for deleted behavior.
+
    **Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or scenarios are vague (e.g., "validates correctly" without naming inputs and expected outcomes), supplement from the unit's own context before writing tests:
 
    | Category | When it applies | How to derive if missing |
@@ -206,7 +233,7 @@ This command takes a work document (plan, specification, or todo file) and execu
    - Run relevant tests after each significant change
    - Don't wait until the end to test
    - Fix failures immediately
-   - Add new tests for new functionality
+   - Add new tests for new behavior, update tests for changed behavior, remove tests for deleted behavior
    - **Unit tests with mocks prove logic in isolation. Integration tests with real objects prove the layers work together.** If your change touches callbacks, middleware, or error handling — you need both.
 
 5. **Simplify as You Go**
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -1,26 +1,50 @@
 ---
 name: ce:work
-description: Execute work plans efficiently while maintaining quality and finishing features
-argument-hint: "[plan file, specification, or todo file path]"
+description: Execute work efficiently while maintaining quality and finishing features
+argument-hint: "[plan file path or description of work to do]"
 ---
 
-# Work Plan Execution Command
+# Work Execution Command
 
-Execute a work plan efficiently while maintaining quality and finishing features.
+Execute work efficiently while maintaining quality and finishing features.
 
 ## Introduction
 
-This command takes a work document (plan, specification, or todo file) and executes it systematically. The focus is on **shipping complete features** by understanding requirements quickly, following existing patterns, and maintaining quality throughout.
+This command takes a work document (plan, specification, or todo file) or a bare prompt describing the work, and executes it systematically. The focus is on **shipping complete features** by understanding requirements quickly, following existing patterns, and maintaining quality throughout.
 
 ## Input Document
 
 <input_document> #$ARGUMENTS </input_document>
 
 ## Execution Workflow
 
+### Phase 0: Input Triage
+
+Determine how to proceed based on what was provided in `<input_document>`.
+
+**Plan document** (input is a file path to an existing plan, specification, or todo file) → skip to Phase 1.
+
+**Bare prompt** (input is a description of work, not a file path):
+
+1. **Scan the work area**
+
+   - Identify files likely to change based on the prompt
+   - Find existing test files for those areas (search for test/spec files that import, reference, or share names with the implementation files)
+   - Note local patterns and conventions in the affected areas
+
+2. **Assess complexity and route**
+
+   | Complexity | Signals | Action |
+   |-----------|---------|--------|
+   | **Trivial** | 1-2 files, no behavioral change (typo, config, rename) | Proceed to Phase 1 step 2 (environment setup), then implement directly — no task list, no execution loop. Apply Test Discovery if the change touches behavior-bearing code |
+   | **Small / Medium** | Clear scope, under ~10 files | Build a task list from discovery. Proceed to Phase 1 step 2 |
+   | **Large** | Cross-cutting, architectural decisions, 10+ files, touches auth/payments/migrations | Inform the user this would benefit from `/ce:brainstorm` or `/ce:plan` to surface edge cases and scope boundaries. Honor their choice. If proceeding, build a task list and continue to Phase 1 step 2 |
+
+---
+
 ### Phase 1: Quick Start
 
-1. **Read Plan and Clarify**
+1. **Read Plan and Clarify** _(skip if arriving from Phase 0 with a bare prompt)_
 
    - Read the work document completely
    - Treat the plan as a decision artifact, not an execution script
@@ -78,7 +102,7 @@ This command takes a work document (plan, specification, or todo file) and execu
    - You want to keep the default branch clean while experimenting
    - You plan to switch between branches frequently
 
-3. **Create Todo List**
+3. **Create Todo List** _(skip if Phase 0 already built one, or if Phase 0 routed as Trivial)_
    - Use your available task tracking tool (e.g., TodoWrite, task lists) to break the plan into actionable tasks
    - Derive tasks from the plan's implementation units, dependencies, files, test targets, and verification criteria
    - Carry each unit's `Execution note` into the task when present
@@ -96,9 +120,9 @@ This command takes a work document (plan, specification, or todo file) and execu
 
    | Strategy | When to use |
    |----------|-------------|
-   | **Inline** | 1-2 small tasks, or tasks needing user interaction mid-flight |
-   | **Serial subagents** | 3+ tasks with dependencies between them. Each subagent gets a fresh context window focused on one unit — prevents context degradation across many tasks |
-   | **Parallel subagents** | 3+ tasks where some units have no shared dependencies and touch non-overlapping files. Dispatch independent units simultaneously, run dependent units after their prerequisites complete |
+   | **Inline** | 1-2 small tasks, or tasks needing user interaction mid-flight. **Default for bare-prompt work** — bare prompts rarely produce enough structured context to justify subagent dispatch |
+   | **Serial subagents** | 3+ tasks with dependencies between them. Each subagent gets a fresh context window focused on one unit — prevents context degradation across many tasks. Requires plan-unit metadata (Goal, Files, Approach, Test scenarios) |
+   | **Parallel subagents** | 3+ tasks where some units have no shared dependencies and touch non-overlapping files. Dispatch independent units simultaneously, run dependent units after their prerequisites complete. Requires plan-unit metadata |
 
    **Subagent dispatch** uses your available subagent or task spawning mechanism. For each unit, give the subagent:
    - The full plan file path (for overall context)
@@ -119,10 +143,11 @@ This command takes a work document (plan, specification, or todo file) and execu
    ```
    while (tasks remain):
      - Mark task as in-progress
-     - Read any referenced files from the plan
+     - Read any referenced files from the plan or discovered during Phase 0
      - Look for similar patterns in codebase
+     - Find existing test files for implementation files being changed (Test Discovery — see below)
      - Implement following existing conventions
-     - Write tests for new functionality
+     - Add, update, or remove tests to match implementation changes (see Test Discovery below)
      - Run System-Wide Test Check (see below)
      - Run tests after changes
      - Mark task as completed
@@ -137,6 +162,8 @@ This command takes a work document (plan, specification, or todo file) and execu
    - Do not over-implement beyond the current behavior slice when working test-first
    - Skip test-first discipline for trivial renames, pure configuration, and pure styling work
 
+   **Test Discovery** — Before implementing changes to a file, find its existing test files (search for test/spec files that import, reference, or share naming patterns with the implementation file). When a plan specifies test scenarios or test files, start there, then check for additional test coverage the plan may not have enumerated. Changes to implementation files should be accompanied by corresponding test updates — new tests for new behavior, modified tests for changed behavior, removed or updated tests for deleted behavior.
+
    **Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or scenarios are vague (e.g., "validates correctly" without naming inputs and expected outcomes), supplement from the unit's own context before writing tests:
 
    | Category | When it applies | How to derive if missing |
@@ -205,7 +232,7 @@ This command takes a work document (plan, specification, or todo file) and execu
    - Run relevant tests after each significant change
    - Don't wait until the end to test
    - Fix failures immediately
-   - Add new tests for new functionality
+   - Add new tests for new behavior, update tests for changed behavior, remove tests for deleted behavior
    - **Unit tests with mocks prove logic in isolation. Integration tests with real objects prove the layers work together.** If your change touches callbacks, middleware, or error handling — you need both.
 
 5. **Simplify as You Go**
PATCH

echo "Gold patch applied."
