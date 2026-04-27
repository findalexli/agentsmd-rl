#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "7. **Carry execution posture lightly when it matters** - If the request, origin " "plugins/compound-engineering/skills/ce-plan-beta/SKILL.md" && grep -qF "When a unit carries an `Execution note`, honor it. For test-first units, write t" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan-beta/SKILL.md b/plugins/compound-engineering/skills/ce-plan-beta/SKILL.md
@@ -35,6 +35,7 @@ Do not proceed until you have a clear planning input.
 4. **Right-size the artifact** - Small work gets a compact plan. Large work gets more structure. The philosophy stays the same at every depth.
 5. **Separate planning from execution discovery** - Resolve planning-time questions here. Explicitly defer execution-time unknowns to implementation.
 6. **Keep the plan portable** - The plan should work as a living document, review artifact, or issue body without embedding tool-specific executor instructions.
+7. **Carry execution posture lightly when it matters** - If the request, origin document, or repo context clearly implies test-first, characterization-first, or another non-default execution posture, reflect that in the plan as a lightweight signal. Do not turn the plan into step-by-step execution choreography.
 
 ## Plan Quality Bar
 
@@ -153,6 +154,19 @@ Collect:
 - AGENTS.md guidance that materially affects the plan, with CLAUDE.md used only as compatibility fallback when present
 - Institutional learnings from `docs/solutions/`
 
+#### 1.1b Detect Execution Posture Signals
+
+Decide whether the plan should carry a lightweight execution posture signal.
+
+Look for signals such as:
+- The user explicitly asks for TDD, test-first, or characterization-first work
+- The origin document calls for test-first implementation or exploratory hardening of legacy code
+- Local research shows the target area is legacy, weakly tested, or historically fragile, suggesting characterization coverage before changing behavior
+
+When the signal is clear, carry it forward silently in the relevant implementation units.
+
+Ask the user only if the posture would materially change sequencing or risk and cannot be responsibly inferred.
+
 #### 1.2 Decide on External Research
 
 Based on the origin document, user signals, and local findings, decide whether external research adds value.
@@ -261,12 +275,20 @@ For each unit, include:
 - **Dependencies** - what must exist first
 - **Files** - exact file paths to create, modify, or test
 - **Approach** - key decisions, data flow, component boundaries, or integration notes
+- **Execution note** - optional, only when the unit benefits from a non-default execution posture such as test-first or characterization-first work
 - **Patterns to follow** - existing code or conventions to mirror
 - **Test scenarios** - specific behaviors, edge cases, and failure paths to cover
 - **Verification** - how an implementer should know the unit is complete, expressed as outcomes rather than shell command scripts
 
 Every feature-bearing unit should include the test file path in `**Files:**`.
 
+Use `Execution note` sparingly. Good uses include:
+- `Execution note: Start with a failing integration test for the request/response contract.`
+- `Execution note: Add characterization coverage before modifying this legacy parser.`
+- `Execution note: Implement new domain behavior test-first.`
+
+Do not expand units into literal `RED/GREEN/REFACTOR` substeps.
+
 #### 3.5 Keep Planning-Time and Implementation-Time Unknowns Separate
 
 If something is important but not knowable yet, record it explicitly under deferred implementation notes rather than pretending to resolve it in the plan.
@@ -392,6 +414,8 @@ deepened: YYYY-MM-DD  # optional, set later by deepen-plan-beta when the plan is
 **Approach:**
 - [Key design or sequencing decision]
 
+**Execution note:** [Optional test-first, characterization-first, or other execution posture signal]
+
 **Patterns to follow:**
 - [Existing file, class, or pattern]
 
@@ -468,6 +492,7 @@ For larger `Deep` plans, extend the core template only when useful with sections
 - Keep implementation units checkable with `- [ ]` syntax for progress tracking
 - Do not include fenced implementation code blocks unless the plan itself is about code shape as a design artifact
 - Do not include git commands, commit messages, or exact test command recipes
+- Do not expand implementation units into micro-step `RED/GREEN/REFACTOR` instructions
 - Do not pretend an execution-time question is settled just to make the plan look complete
 - Include mermaid diagrams when they clarify relationships or flows that prose alone would make hard to follow — ERDs for data model changes, sequence diagrams for multi-service interactions, state diagrams for lifecycle transitions, flowcharts for complex branching logic
 
@@ -480,6 +505,7 @@ Before finalizing, check:
 - If there was no origin document, the bounded planning bootstrap established enough product clarity to plan responsibly
 - Every major decision is grounded in the origin document or research
 - Each implementation unit is concrete, dependency-ordered, and implementation-ready
+- If test-first or characterization-first posture was explicit or strongly implied, the relevant units carry it forward with a lightweight `Execution note`
 - Test scenarios are specific without becoming test code
 - Deferred items are explicit and not hidden as fake certainty
 
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -25,9 +25,11 @@ This command takes a work document (plan, specification, or todo file) and execu
    - Read the work document completely
    - Treat the plan as a decision artifact, not an execution script
    - If the plan includes sections such as `Implementation Units`, `Work Breakdown`, `Requirements Trace`, `Files`, `Test Scenarios`, or `Verification`, use those as the primary source material for execution
+   - Check for `Execution note` on each implementation unit — these carry the plan's execution posture signal for that unit (for example, test-first or characterization-first). Note them when creating tasks.
    - Check for a `Deferred to Implementation` or `Implementation-Time Unknowns` section — these are questions the planner intentionally left for you to resolve during execution. Note them before starting so they inform your approach rather than surprising you mid-task
    - Check for a `Scope Boundaries` section — these are explicit non-goals. Refer back to them if implementation starts pulling you toward adjacent work
    - Review any references or links provided in the plan
+   - If the user explicitly asks for TDD, test-first, or characterization-first execution in this session, honor that request even if the plan has no `Execution note`
    - If anything is unclear or ambiguous, ask clarifying questions now
    - Get user approval to proceed
    - **Do not skip this** - better to ask questions now than build the wrong thing
@@ -79,6 +81,7 @@ This command takes a work document (plan, specification, or todo file) and execu
 3. **Create Todo List**
    - Use your available task tracking tool (e.g., TodoWrite, task lists) to break the plan into actionable tasks
    - Derive tasks from the plan's implementation units, dependencies, files, test targets, and verification criteria
+   - Carry each unit's `Execution note` into the task when present
    - For each unit, read the `Patterns to follow` field before implementing — these point to specific files or conventions to mirror
    - Use each unit's `Verification` field as the primary "done" signal for that task
    - Do not expect the plan to contain implementation code, micro-step TDD instructions, or exact shell commands
@@ -99,7 +102,7 @@ This command takes a work document (plan, specification, or todo file) and execu
 
    **Subagent dispatch** uses your available subagent or task spawning mechanism. For each unit, give the subagent:
    - The full plan file path (for overall context)
-   - The specific unit's Goal, Files, Approach, Patterns, Test scenarios, and Verification
+   - The specific unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, and Verification
    - Any resolved deferred questions relevant to that unit
 
    After each subagent completes, update the plan checkboxes and task list before dispatching the next dependent unit.
@@ -125,6 +128,14 @@ This command takes a work document (plan, specification, or todo file) and execu
      - Evaluate for incremental commit (see below)
    ```
 
+   When a unit carries an `Execution note`, honor it. For test-first units, write the failing test before implementation for that unit. For characterization-first units, capture existing behavior before changing it. For units without an `Execution note`, proceed pragmatically.
+
+   Guardrails for execution posture:
+   - Do not write the test and implementation in the same step when working test-first
+   - Do not skip verifying that a new test fails before implementing the fix or feature
+   - Do not over-implement beyond the current behavior slice when working test-first
+   - Skip test-first discipline for trivial renames, pure configuration, and pure styling work
+
    **System-Wide Test Check** — Before marking a task done, pause and ask:
 
    | Question | What to do |
PATCH

echo "Gold patch applied."
