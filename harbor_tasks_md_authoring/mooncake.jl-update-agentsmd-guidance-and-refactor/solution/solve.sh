#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mooncake.jl

# Idempotency guard
if grep -qF "Inspects Mooncake's internal AD pipeline only. For allocation, world-age, or com" ".claude/skills/inspect/SKILL.md" && grep -qF ".claude/skills/ir-inspect/SKILL.md" ".claude/skills/ir-inspect/SKILL.md" && grep -qF "description: Prune a bug fix or new tests down to the smallest correct diff thro" ".claude/skills/minimise/SKILL.md" && grep -qF "- Use the canonical test utilities: `Mooncake.TestUtils.test_rule` for new diffe" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/inspect/SKILL.md b/.claude/skills/inspect/SKILL.md
@@ -0,0 +1,90 @@
+---
+name: inspect
+description: Inspect the AD pipeline IR for a Julia function at each Mooncake compilation stage.
+---
+
+# Inspect
+
+Inspect IR transformations in Mooncake's AD pipeline for a given function.
+
+## Setup
+
+```julia
+using Mooncake, Mooncake.SkillUtils
+```
+
+## Gathering user intent
+
+Ask the user:
+
+1. **Function and arguments** — e.g. `sin, 1.0` or a custom function
+2. **Mode** — reverse (default) or forward
+3. **What to view** — all stages, a specific stage, a diff between two stages, or world age info
+
+Do not assume — ask the user to pick.
+
+## Pipeline stages
+
+### Reverse mode (default)
+| Stage | Symbol | Description |
+|-------|--------|-------------|
+| Raw IR | `:raw` | optimised, type-inferred SSAIR from Julia's compiler |
+| Normalised | `:normalized` | after Mooncake's normalisation passes |
+| BBCode | `:bbcode` | BBCode representation with stable IDs |
+| Forward IR | `:fwd_ir` | generated forward-pass IR |
+| Reverse IR | `:rvs_ir` | generated pullback IR |
+| Optimised Forward | `:optimized_fwd` | forward pass after optimisation |
+| Optimised Reverse | `:optimized_rvs` | pullback after optimisation |
+
+### Forward mode
+| Stage | Symbol | Description |
+|-------|--------|-------------|
+| Raw IR | `:raw` | optimised, type-inferred SSAIR from Julia's compiler |
+| Normalised | `:normalized` | after Mooncake's normalisation passes |
+| BBCode | `:bbcode` | inspection-only — forward mode does not use BBCode internally |
+| Dual IR | `:dual_ir` | generated dual-number IR |
+| Optimised | `:optimized` | after optimisation passes |
+
+## Commands
+
+```julia
+# Full inspection
+ins = inspect_ir(f, args...; mode=:reverse)  # or mode=:forward
+
+# View stages
+show_ir(ins)                          # all stages
+show_stage(ins, :raw)                 # one stage
+
+# Diffs between stages
+show_diff(ins; from=:raw, to=:normalized)
+show_all_diffs(ins)
+
+# World age debugging
+show_world_info(ins)
+
+# Write everything to files
+write_ir(ins, "/tmp/ir_output")
+
+# Shorthand helpers
+ins = inspect_fwd(f, args...)         # forward mode
+ins = inspect_rvs(f, args...)         # reverse mode
+ins = quick_inspect(f, args...)       # inspect + display immediately
+
+# Options
+inspect_ir(f, args...;
+    mode       = :reverse,
+    optimize   = true,
+    do_inline  = true,
+    debug_mode = false,
+)
+```
+
+## Presenting results
+
+- Run commands via Bash and present IR in fenced code blocks.
+- When showing diffs, explain what changed and why the transformation matters.
+- If errors occur, check that Mooncake is loaded and the function signature is valid.
+
+## Limitations
+
+Inspects Mooncake's internal AD pipeline only. For allocation, world-age, or compiler-boundary debugging, see `docs/src/developer_documentation/advanced_debugging.md`.
diff --git a/.claude/skills/ir-inspect/SKILL.md b/.claude/skills/ir-inspect/SKILL.md
@@ -1,103 +0,0 @@
----
-name: ir-inspect
-description: Inspect Mooncake.jl IR transformations at each stage of the AD pipeline. Use when the user wants to view, debug, or understand IR at any compilation stage.
----
-
-# Mooncake IR Inspection
-
-You are helping the user inspect IR (Intermediate Representation) transformations in Mooncake.jl's automatic differentiation pipeline.
-
-## Setup
-
-The IR inspection functions are part of Mooncake.jl. Start a Julia session and load the package:
-
-```julia
-using Mooncake
-using Mooncake.SkillUtils
-```
-
-All functions below are defined in the `Mooncake.SkillUtils` module.
-
-## Gathering user intent
-
-Ask the user what they want to inspect. Offer these choices:
-
-1. **Function to inspect** — ask which function and arguments (e.g. `sin, 1.0` or a custom function)
-2. **Mode** — reverse mode (default) or forward mode
-3. **What to view**:
-   - All stages at once
-   - A specific stage
-   - A diff between two stages
-   - World age info
-
-Do not assume — ask the user to pick.
-
-## Pipeline stages
-
-### Reverse mode stages (default)
-| Stage | Symbol | Description |
-|-------|--------|-------------|
-| Raw IR | `:raw` | optimised, type-infered SSAIR from Julia's compiler |
-| Normalized | `:normalized` | After Mooncake's normalization passes |
-| BBCode | `:bbcode` | BBCode representation with stable IDs |
-| Forward IR | `:fwd_ir` | Generated forward-pass IR |
-| Reverse IR | `:rvs_ir` | Generated pullback (reverse-pass) IR |
-| Optimized Forward | `:optimized_fwd` | Forward pass after optimization |
-| Optimized Reverse | `:optimized_rvs` | Pullback after optimization |
-
-### Forward mode stages
-| Stage | Symbol | Description |
-|-------|--------|-------------|
-| Raw IR | `:raw` | optimised, type-infered SSAIR from Julia's compiler |
-| Normalized | `:normalized` | After Mooncake's normalization passes |
-| BBCode | `:bbcode` | Inspection-only — forward mode does not use BBCode internally |
-| Dual IR | `:dual_ir` | Generated dual-number IR |
-| Optimized | `:optimized` | After optimization passes |
-
-## Commands reference
-
-```julia
-using Mooncake
-using Mooncake.SkillUtils
-
-# Full inspection
-ins = inspect_ir(f, args...; mode=:reverse)  # or mode=:forward
-
-# View stages
-show_ir(ins)                          # all stages
-show_stage(ins, :raw)                 # one stage
-
-# Diffs between stages
-show_diff(ins; from=:raw, to=:normalized)
-show_all_diffs(ins)
-
-# World age debugging
-show_world_info(ins)
-
-# Write everything to files
-write_ir(ins, "/tmp/ir_output")
-
-# Shorthand helpers
-ins = inspect_fwd(f, args...)         # forward mode
-ins = inspect_rvs(f, args...)         # reverse mode
-ins = quick_inspect(f, args...)       # inspect + display immediately
-
-# Options
-inspect_ir(f, args...;
-    mode       = :reverse,
-    optimize   = true,
-    do_inline  = true,
-    debug_mode = false,
-)
-```
-
-## How to present results
-
-- Run the Julia commands via Bash and capture output.
-- Present the IR text in fenced code blocks with context about what each stage represents.
-- When showing diffs, highlight what changed and explain why the transformation matters.
-- If errors occur, check that Mooncake is loaded and the function signature is valid.
-
-## Limitations
-
-This skill inspects Mooncake's **internal AD pipeline** — the IR it generates for forward/reverse passes. For debugging beyond IR (allocations, world age, compiler boundary), see `docs/src/developer_documentation/advanced_debugging.md`.
diff --git a/.claude/skills/minimise/SKILL.md b/.claude/skills/minimise/SKILL.md
@@ -0,0 +1,48 @@
+---
+name: minimise
+description: Prune a bug fix or new tests down to the smallest correct diff through multiple elimination passes. Use before committing any fix or test addition.
+---
+
+# Minimise
+
+The goal is to remove every line that is not strictly required for correctness,
+then verify the result still passes the relevant tests.
+
+## Process
+
+Repeat the following until no further reductions are possible:
+
+1. **Read the diff.** Run `git diff HEAD` (or `git diff --cached` if staged) and
+   read every changed file in full.
+
+2. **Challenge each change.** For every changed line ask:
+   - Would removing this line cause a test to fail or a bug to reappear?
+   - Is this a cleanup, rename, refactor, or comment that is not load-bearing?
+   - For new tests: does an existing test already cover this behaviour?
+     If so, drop the new test entirely.
+
+3. **Remove non-essential changes.** Delete anything that does not answer
+   "yes" to the first question above. Prefer shrinking an existing case over
+   adding a new one.
+
+4. **Run the minimal test group.** Use the smallest focused test group that
+   exercises the changed code (see `test/runtests.jl` for group names).
+   Confirm all tests pass before continuing.
+
+5. **Repeat** from step 1 until a full pass produces no further removals.
+
+## Heuristics
+
+- A one-line fix is better than a five-line fix.
+- A new test case added to an existing `@testset` is better than a new `@testset`.
+- A new value constructor in `src/test_resources.jl` should be the minimum needed
+  to instantiate the type under test; no extra fields or variants.
+- Comments and blank lines added alongside a fix are not load-bearing; remove them
+  unless they explain something non-obvious.
+- Helper functions introduced solely for the fix are a red flag; inline them.
+
+## When to stop
+
+Stop when every remaining line answers "yes" to: *if I remove this, the targeted
+bug reappears or the targeted test fails*. At that point report the final diff and
+suggest committing.
diff --git a/AGENTS.md b/AGENTS.md
@@ -50,7 +50,7 @@ The overall target is: correct by construction where possible, aggressively test
 - If you change public APIs, developer tooling, or core internals, update docs under `docs/src/` when needed.
 - Prefer targeted changes over broad refactors unless the task explicitly requires restructuring.
 - Prefer clear, concise names for variables, types, and methods.
-- When fixing bugs or performance issues (allocations, type instability), prefer minimal inline fixes rather than introducing new helper functions.
+- When fixing bugs or performance issues (allocations, type instability), prefer minimal inline fixes over new helper functions; make multiple pruning passes before committing to arrive at the smallest correct diff. Use the `minimise` skill before committing.
 
 ## Consistency
 
@@ -61,13 +61,13 @@ The overall target is: correct by construction where possible, aggressively test
 ## Testing
 
 - Prefer constructing a minimal working example (MWE) first, then running the smallest focused test group that validates the fix, and only then broader test groups if needed.
-- For new differentiation rules, prefer testing them with `Mooncake.TestUtils.test_rule`.
+- Before adding a new test or test helper, check whether the behaviour is already covered; prefer extending an existing case over introducing a new one, make multiple pruning passes, and keep additions minimal.
+- Use the canonical test utilities: `Mooncake.TestUtils.test_rule` for new differentiation rules; `TestUtils.test_tangent_splitting` on a concrete value (add constructors to `src/test_resources.jl`) for tangent/fdata/rdata correctness rather than direct `@test tangent_type(...)` assertions; `TestUtils.test_data` for custom tangent type implementations.
 - Do not disable tests or weaken performance assertions just to get CI green; if that appears necessary, stop and ask for confirmation first.
 - Ensure supported primal types and their tangent types are exercised against the relevant rules for compatibility and composability.
 - Mooncake has a debug mode which is useful for testing malformed rules and diagnosing rule failures; see `docs/src/utilities/debug_mode.md`.
 - For performance-sensitive rules, verify by running the `frule!!` or `rrule!!` directly and checking allocations and runtime against the primal. Use `@allocated` to ensure that zero-allocation primals still yield zero-allocation AD paths, and `@code_warntype` to check for type stability.
-- Bug fixes in rules, the interpreter, or compiler interop should ideally land with a focused regression test.
-- If a fix depends on compiler or world-age behaviour, isolate it and test it directly.
+- Bug fixes should land with a focused regression test; if the fix depends on compiler or world-age behaviour, isolate it and test directly.
 - `friendly_tangents` can display a misleading value for structured or wrapped types even when the underlying tangent data is correct. Do not treat a surprising `friendly_tangents` result as proof of a bug without also inspecting the raw tangent.
 - `src/test_resources.jl` is shared test infrastructure, not dead code. It feeds broad interpreter/rule tests indirectly via `TestResources.generate_test_functions()`, so do not judge it by one-file-one-test symmetry.
 - Treat `temp/` as local scratch space, preferably untracked. Put ad hoc experiments, scratch scripts, and debugging MWEs there rather than in source or test files.
PATCH

echo "Gold patch applied."
