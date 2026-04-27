#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "When modifying a skill that has a `-beta` counterpart (or vice versa), always ch" "plugins/compound-engineering/AGENTS.md" && grep -qF "- **Test scenarios** - enumerate the specific test cases the implementer should " "plugins/compound-engineering/skills/ce-plan/SKILL.md" && grep -qF "**Test Scenario Completeness** \u2014 Before writing tests for a feature-bearing unit" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "**Test Scenario Completeness** \u2014 Before writing tests for a feature-bearing unit" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/AGENTS.md b/plugins/compound-engineering/AGENTS.md
@@ -158,6 +158,10 @@ Some skills are exact copies from external upstream repositories, vendored local
 
 Beta skills use a `-beta` suffix and `disable-model-invocation: true` to prevent accidental auto-triggering. See `docs/solutions/skill-design/beta-skills-framework.md` for naming, validation, and promotion rules.
 
+### Stable/Beta Sync
+
+When modifying a skill that has a `-beta` counterpart (or vice versa), always check the other version and **state your sync decision explicitly** before committing — e.g., "Propagated to beta — shared test guidance" or "Not propagating — this is the experimental delegate mode beta exists to test." Syncing to both, stable-only, and beta-only are all valid outcomes. The goal is deliberate reasoning, not a default rule.
+
 ## Documentation
 
 See `docs/solutions/plugin-versioning-requirements.md` for detailed versioning workflow.
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -45,7 +45,7 @@ Every plan should contain:
 - Explicit test file paths for feature-bearing implementation units
 - Decisions with rationale, not just tasks
 - Existing patterns or code references to follow
-- Specific test scenarios and verification outcomes
+- Enumerated test scenarios for each feature-bearing unit, specific enough that an implementer knows exactly what to test without inventing coverage themselves
 - Clear dependencies and sequencing
 
 A plan is ready when an implementer can start confidently without needing the plan to write the code for them.
@@ -335,7 +335,11 @@ For each unit, include:
 - **Execution note** - optional, only when the unit benefits from a non-default execution posture such as test-first, characterization-first, or external delegation
 - **Technical design** - optional pseudo-code or diagram when the unit's approach is non-obvious and prose alone would leave it ambiguous. Frame explicitly as directional guidance, not implementation specification
 - **Patterns to follow** - existing code or conventions to mirror
-- **Test scenarios** - specific behaviors, edge cases, and failure paths to cover
+- **Test scenarios** - enumerate the specific test cases the implementer should write, right-sized to the unit's complexity and risk. Consider each category below and include scenarios from every category that applies to this unit. A simple config change may need one scenario; a payment flow may need a dozen. The quality signal is specificity — each scenario should name the input, action, and expected outcome so the implementer doesn't have to invent coverage.
+  - **Happy path behaviors** - core functionality with expected inputs and outputs
+  - **Edge cases** (when the unit has meaningful boundaries) - boundary values, empty inputs, nil/null states, concurrent access
+  - **Error and failure paths** (when the unit has failure modes) - invalid input, downstream service failures, timeout behavior, permission denials
+  - **Integration scenarios** (when the unit crosses layers) - behaviors that mocks alone will not prove, e.g., "creating X triggers callback Y which persists Z". Include these for any unit touching callbacks, middleware, or multi-layer interactions
 - **Verification** - how an implementer should know the unit is complete, expressed as outcomes rather than shell command scripts
 
 Every feature-bearing unit should include the test file path in `**Files:**`.
@@ -491,8 +495,8 @@ deepened: YYYY-MM-DD  # optional, set when the confidence check substantively st
 - [Existing file, class, or pattern]
 
 **Test scenarios:**
-- [Specific scenario with expected behavior]
-- [Edge case or failure path]
+<!-- Include only categories that apply to this unit. Omit categories that don't. -->
+- [Scenario: specific input/action -> expected outcome. Prefix with category — Happy path, Edge case, Error path, or Integration — to signal intent]
 
 **Verification:**
 - [Outcome that should hold when this unit is complete]
@@ -578,7 +582,8 @@ Before finalizing, check:
 - Every major decision is grounded in the origin document or research
 - Each implementation unit is concrete, dependency-ordered, and implementation-ready
 - If test-first or characterization-first posture was explicit or strongly implied, the relevant units carry it forward with a lightweight `Execution note`
-- Test scenarios are specific without becoming test code
+- Each feature-bearing unit has test scenarios from every applicable category (happy path, edge cases, error paths, integration) — right-sized to the unit's complexity, not padded or skimped
+- Test scenarios name specific inputs, actions, and expected outcomes without becoming test code
 - Deferred items are explicit and not hidden as fake certainty
 - If a High-Level Technical Design section is included, it uses the right medium for the work, carries the non-prescriptive framing, and does not contain implementation code (no imports, exact signatures, or framework-specific syntax)
 - Per-unit technical design fields, if present, are concise and directional rather than copy-paste-ready
@@ -703,7 +708,8 @@ If the plan already has a `deepened:` date:
 - File paths or test file paths are missing where they should be explicit
 - Units are too large, too vague, or broken into micro-steps
 - Approach notes are thin or do not name the pattern to follow
-- Test scenarios or verification outcomes are vague
+- Test scenarios are vague (don't name inputs and expected outcomes), skip applicable categories (e.g., no error paths for a unit with failure modes, no integration scenarios for a unit crossing layers), or are disproportionate to the unit's complexity
+- Verification outcomes are vague or not expressed as observable results
 
 **System-Wide Impact**
 - Affected interfaces, callbacks, middleware, entry points, or parity surfaces are missing
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -105,6 +105,7 @@ This command takes a work document (plan, specification, or todo file) and execu
    - The full plan file path (for overall context)
    - The specific unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, and Verification
    - Any resolved deferred questions relevant to that unit
+   - Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests
 
    After each subagent completes, update the plan checkboxes and task list before dispatching the next dependent unit.
 
@@ -137,6 +138,15 @@ This command takes a work document (plan, specification, or todo file) and execu
    - Do not over-implement beyond the current behavior slice when working test-first
    - Skip test-first discipline for trivial renames, pure configuration, and pure styling work
 
+   **Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or scenarios are vague (e.g., "validates correctly" without naming inputs and expected outcomes), supplement from the unit's own context before writing tests:
+
+   | Category | When it applies | How to derive if missing |
+   |----------|----------------|------------------------|
+   | **Happy path** | Always for feature-bearing units | Read the unit's Goal and Approach for core input/output pairs |
+   | **Edge cases** | When the unit has meaningful boundaries (inputs, state, concurrency) | Identify boundary values, empty/nil inputs, and concurrent access patterns |
+   | **Error/failure paths** | When the unit has failure modes (validation, external calls, permissions) | Enumerate invalid inputs the unit should reject, permission/auth denials it should enforce, and downstream failures it should handle |
+   | **Integration** | When the unit crosses layers (callbacks, middleware, multi-service) | Identify the cross-layer chain and write a scenario that exercises it without mocks |
+
    **System-Wide Test Check** — Before marking a task done, pause and ask:
 
    | Question | What to do |
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -104,6 +104,7 @@ This command takes a work document (plan, specification, or todo file) and execu
    - The full plan file path (for overall context)
    - The specific unit's Goal, Files, Approach, Execution note, Patterns, Test scenarios, and Verification
    - Any resolved deferred questions relevant to that unit
+   - Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests
 
    After each subagent completes, update the plan checkboxes and task list before dispatching the next dependent unit.
 
@@ -136,6 +137,15 @@ This command takes a work document (plan, specification, or todo file) and execu
    - Do not over-implement beyond the current behavior slice when working test-first
    - Skip test-first discipline for trivial renames, pure configuration, and pure styling work
 
+   **Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or scenarios are vague (e.g., "validates correctly" without naming inputs and expected outcomes), supplement from the unit's own context before writing tests:
+
+   | Category | When it applies | How to derive if missing |
+   |----------|----------------|------------------------|
+   | **Happy path** | Always for feature-bearing units | Read the unit's Goal and Approach for core input/output pairs |
+   | **Edge cases** | When the unit has meaningful boundaries (inputs, state, concurrency) | Identify boundary values, empty/nil inputs, and concurrent access patterns |
+   | **Error/failure paths** | When the unit has failure modes (validation, external calls, permissions) | Enumerate invalid inputs the unit should reject, permission/auth denials it should enforce, and downstream failures it should handle |
+   | **Integration** | When the unit crosses layers (callbacks, middleware, multi-service) | Identify the cross-layer chain and write a scenario that exercises it without mocks |
+
    **System-Wide Test Check** — Before marking a task done, pause and ask:
 
    | Question | What to do |
PATCH

echo "Gold patch applied."
