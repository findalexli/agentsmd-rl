#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "**Tier 2: Full review (default)** \u2014 REQUIRED unless Tier 1 criteria are explicit" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "**Tier 2: Full review (default)** \u2014 REQUIRED unless Tier 1 criteria are explicit" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -291,18 +291,18 @@ Determine how to proceed based on what was provided in `<input_document>`.
    # Use linting-agent before pushing to origin
    ```
 
-2. **Code Review**
+2. **Code Review** (REQUIRED)
 
-   Every change gets reviewed before shipping. The depth scales with the change's risk profile.
+   Every change gets reviewed before shipping. The depth scales with the change's risk profile, but review itself is never skipped.
 
-   **Tier 1: Inline self-review** — Read the diff and check for logic errors, missed edge cases, and plan drift. No specialized agents. Use this tier only when **all four** criteria are true:
+   **Tier 2: Full review (default)** — REQUIRED unless Tier 1 criteria are explicitly met. Invoke the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and surface residual work as todos. When the plan file path is known, pass it as `plan:<path>`. This is the mandatory default — proceed to Tier 1 only after confirming every criterion below.
+
+   **Tier 1: Inline self-review** — A lighter alternative permitted only when **all four** criteria are true. Before choosing Tier 1, explicitly state which criteria apply and why. If any criterion is uncertain, use Tier 2.
    - Purely additive (new files only, no existing behavior modified)
    - Single concern (one skill, one component — not cross-cutting)
    - Pattern-following (implementation mirrors an existing example with no novel logic)
    - Plan-faithful (no scope growth, no deferred questions resolved with surprising answers)
 
-   **Tier 2: Full review (default)** — Load the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and surface residual work as todos. When the plan file path is known, pass it as `plan:<path>`. This is the default when working from a plan — use it unless all four Tier 1 criteria are met.
-
 3. **Final Validation**
    - All tasks marked completed
    - Testing addressed -- tests pass and new/changed behavior has corresponding test coverage (or an explicit justification for why tests are not needed)
@@ -528,14 +528,14 @@ Before creating PR, verify:
 
 Every change gets reviewed. The tier determines depth, not whether review happens.
 
-**Tier 1 (inline self-review)** — all four must be true:
+**Tier 2 (full review)** — REQUIRED default. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos. Always use this tier unless all four Tier 1 criteria are explicitly confirmed.
+
+**Tier 1 (inline self-review)** — permitted only when all four are true (state each explicitly before choosing):
 - Purely additive (new files only, no existing behavior modified)
 - Single concern (one skill, one component — not cross-cutting)
 - Pattern-following (mirrors an existing example, no novel logic)
 - Plan-faithful (no scope growth, no surprising deferred-question resolutions)
 
-**Tier 2 (full review)** — the default when working from a plan. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos.
-
 ## Common Pitfalls to Avoid
 
 - **Analysis paralysis** - Don't overthink, read the plan and execute
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -282,18 +282,18 @@ Determine how to proceed based on what was provided in `<input_document>`.
    # Use linting-agent before pushing to origin
    ```
 
-2. **Code Review**
+2. **Code Review** (REQUIRED)
 
-   Every change gets reviewed before shipping. The depth scales with the change's risk profile.
+   Every change gets reviewed before shipping. The depth scales with the change's risk profile, but review itself is never skipped.
 
-   **Tier 1: Inline self-review** — Read the diff and check for logic errors, missed edge cases, and plan drift. No specialized agents. Use this tier only when **all four** criteria are true:
+   **Tier 2: Full review (default)** — REQUIRED unless Tier 1 criteria are explicitly met. Invoke the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and surface residual work as todos. When the plan file path is known, pass it as `plan:<path>`. This is the mandatory default — proceed to Tier 1 only after confirming every criterion below.
+
+   **Tier 1: Inline self-review** — A lighter alternative permitted only when **all four** criteria are true. Before choosing Tier 1, explicitly state which criteria apply and why. If any criterion is uncertain, use Tier 2.
    - Purely additive (new files only, no existing behavior modified)
    - Single concern (one skill, one component — not cross-cutting)
    - Pattern-following (implementation mirrors an existing example with no novel logic)
    - Plan-faithful (no scope growth, no deferred questions resolved with surprising answers)
 
-   **Tier 2: Full review (default)** — Load the `ce:review` skill with `mode:autofix` to run specialized reviewer agents, auto-apply safe fixes, and surface residual work as todos. When the plan file path is known, pass it as `plan:<path>`. This is the default when working from a plan — use it unless all four Tier 1 criteria are met.
-
 3. **Final Validation**
    - All tasks marked completed
    - Testing addressed -- tests pass and new/changed behavior has corresponding test coverage (or an explicit justification for why tests are not needed)
@@ -455,14 +455,14 @@ Before creating PR, verify:
 
 Every change gets reviewed. The tier determines depth, not whether review happens.
 
-**Tier 1 (inline self-review)** — all four must be true:
+**Tier 2 (full review)** — REQUIRED default. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos. Always use this tier unless all four Tier 1 criteria are explicitly confirmed.
+
+**Tier 1 (inline self-review)** — permitted only when all four are true (state each explicitly before choosing):
 - Purely additive (new files only, no existing behavior modified)
 - Single concern (one skill, one component — not cross-cutting)
 - Pattern-following (mirrors an existing example, no novel logic)
 - Plan-faithful (no scope growth, no surprising deferred-question resolutions)
 
-**Tier 2 (full review)** — the default when working from a plan. Invoke `ce:review mode:autofix` with `plan:<path>` when available. Safe fixes are applied automatically; residual work surfaces as todos.
-
 ## Common Pitfalls to Avoid
 
 - **Analysis paralysis** - Don't overthink, read the plan and execute
PATCH

echo "Gold patch applied."
