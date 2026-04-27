#!/usr/bin/env bash
set -euo pipefail

cd /workspace/godogen

# Idempotency guard
if grep -qF "- **Requirements** \u2014 high-level behaviors the task must achieve. Focus on *what*" ".claude/agents/game-decomposer.md" && grep -qF "Keep a `**Status:**` field on each task in PLAN.md: `pending` | `in_progress` | " ".claude/agents/gamedev.md" && grep -qF "- **Visual quality & logic:** look for obvious bugs \u2014 geometry clipping through " ".claude/agents/godot-task.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/game-decomposer.md b/.claude/agents/game-decomposer.md
@@ -66,8 +66,8 @@ Produce `{project_root}/PLAN.md`:
 - **Depends on:** (none)
 - **Goal:** {What this task achieves and why it matters}
 - **Requirements:**
-  - {Concrete, testable requirement}
-  - {Concrete, testable requirement}
+  - {High-level, testable behavior — what the player should experience}
+  - {High-level, testable behavior — what the player should experience}
 - **Placeholder:** {Minimal environment to test in isolation. Must exercise the real challenge, not dodge it.}
 - **Verify:** {What screenshots should show. Specific and unambiguous.}
 - **Targets:** scenes/{x}.tscn, scripts/{y}.gd
@@ -76,17 +76,13 @@ Produce `{project_root}/PLAN.md`:
 - **Depends on:** 1
 - ...
 
-### 3. {Merge: X + Y}
-- **Depends on:** 1, 2
-- **Goal:** Integrate {X} with {Y}. Focus: {the specific integration risk}.
-- ...
 ````
 
 ### Task Fields
 
 - **Depends on** — task numbers that must complete before this starts. `(none)` for root tasks.
 - **Goal** — what this task achieves and why it matters for the game.
-- **Requirements** — concrete, testable behaviors. Include dimensions, physics values, colors — everything the generator needs to produce the right output without guessing.
+- **Requirements** — high-level behaviors the task must achieve. Focus on *what* the player experiences, not *how* to implement it. The task executor is a strong LLM — it doesn't need pixel-exact dimensions or implementation recipes. Specify concrete values only when they matter for game feel (e.g., "car should feel heavy, not twitchy") or correctness (e.g., "arena is 50m wide to fit 4 players").
 - **Placeholder** — minimal throwaway environment to test this feature in isolation. Must exercise the real challenge, not avoid it. `(none)` for merge tasks that inherit real environments.
 - **Verify** — a concrete visual scenario for the test harness. The task executor generates a SceneTree script from this: it loads the scene, positions a camera, captures screenshots via `xvfb-run --write-movie`, and compares to this description. Must include: scene to load, camera position/angle, what objects are visible, expected state. Example: "Load arena.tscn. Camera at (0, 15, 10) looking at origin, -45° pitch. Green ground plane fills lower half. Capsule (player) at center. 3 red cubes spaced around edges."
 - **Targets** — scenes and scripts this task creates or modifies.
@@ -115,9 +111,9 @@ A placeholder that avoids the hard part gives false confidence.
 
 Two features are independent when they don't share runtime state and can each be tested with their own placeholder. Make them separate tasks with no dependency. When task A fails and needs regeneration, task B is unaffected.
 
-### Merge Progressively
+### Merge Tasks Are Rarely Needed
 
-Merge tasks integrate previously-independent features. Integrate 2-3 things at a time (A+B → AB, then AB+C → ABC), not everything at once. Merge requirements focus on **integration behavior** ("bullets fired by player damage enemies"), not re-specifying individual features. Note potential friction points.
+Each task builds directly into the shared project — features are integrated by default. Only add a merge task when integration is genuinely non-trivial (e.g., two large independent systems with complex runtime interactions). If the "merge" is just loading scenes together or connecting signals, put that in the later task's requirements instead.
 
 ### Group Coherent Behaviors
 
@@ -144,13 +140,14 @@ Include: scene to load, camera setup, and what the screenshots must show. The ta
 Before outputting, verify:
 
 1. **Hard tasks have clean isolation** — complex features are independent early tasks, not buried behind easy ones
-2. **Merges are progressive** — integrate 2-3 things per merge, not everything at once
+2. **No unnecessary merge tasks** — most simple games need zero
 3. **Placeholders exercise real challenges** — no flat planes for games about terrain
 4. **Every Verify is test-harness-ready** — concrete visual scenario with camera position, visible objects, and expected state
 5. **All assets assigned** — every available asset appears in the Assets table with a task
 
 ## What NOT to Include
 
 - GDScript code or implementation details (task executor handles that)
+- Detailed technical specs — the task executor is a strong LLM, it makes good implementation decisions on its own. Focus on *what* each task should achieve, not *how*.
 - Untestable requirements (everything must be visually verifiable via screenshots)
 - Artificial dependencies between actually-independent features
diff --git a/.claude/agents/gamedev.md b/.claude/agents/gamedev.md
@@ -32,6 +32,10 @@ Scaffold and decomposer work for both fresh projects and updates. When updating,
 
 ```
 User request
+    |
+    +- Check if build/PLAN.md exists (resume check)
+    |   +- If yes: read PLAN.md, STRUCTURE.md, MEMORY.md → skip to task execution
+    |   +- If no: continue with fresh pipeline below
     |
     +- Read build/assets.json (if exists)
     |
@@ -48,10 +52,12 @@ User request
     +- Create CLI todo list from PLAN.md tasks (TodoWrite)
     |
     +- For each task (one at a time, in topological order):
+    |   +- Update PLAN.md: mark task status → in_progress
     |   +- Mark task in_progress (TodoWrite)
     |   +- Launch godot-task sub-agent (see Running Tasks)
     |   +- Read sub-agent result — check for success/failure
     |   +- Handle result (see Handling Task Results below)
+    |   +- Update PLAN.md: mark task status → done / done (partial) / skipped
     |   +- Mark task completed (TodoWrite)
     |   +- Summarize result to user
     |
@@ -142,10 +148,18 @@ If a task reports failure or you suspect integration issues:
 - Read screenshots in `build/test/screenshots/{task_folder}/`
 - Run `cd build && timeout 30 godot --headless --quit 2>&1` to check cross-project compilation
 
+## PLAN.md Task Status
+
+Keep a `**Status:**` field on each task in PLAN.md: `pending` | `in_progress` | `done` | `done (partial)` | `skipped`. Update it immediately when state changes — before launching the sub-agent and after reading its result. This is what enables resumption.
+
+## Resuming an Interrupted Pipeline
+
+At the start of every run, check if `build/PLAN.md` exists. If so, read it along with STRUCTURE.md and MEMORY.md, then resume from the first non-`done` task. Treat `in_progress` as needing a retry.
+
 ## Document Maintenance
 
 **STRUCTURE.md** — scaffold agent is the primary author. Between scaffold runs, you may tweak it when tasks change the inter-file graph (new scene/script, new signal, changed node type, new input action).
 
-**PLAN.md** — decomposer agent is the primary author. Between decomposer runs, you may tweak it when discoveries change future tasks (adjust approach, mark tasks cut, add tasks).
+**PLAN.md** — decomposer agent is the primary author. You own the `**Status:**` fields. Between decomposer runs, you may also tweak tasks when discoveries change future work (adjust approach, mark tasks skipped, add tasks).
 
 Task execution writes discoveries to `build/MEMORY.md`. Check it when a task fails.
diff --git a/.claude/agents/godot-task.md b/.claude/agents/godot-task.md
@@ -27,7 +27,10 @@ The caller specifies `{project_root}` (e.g. `project_root=build`). All files liv
 6. **Fix errors** — if Godot reports errors, read output, fix files, re-run. Repeat until clean.
 7. **Generate test harness** — write `{project_root}/test/test_task.gd` implementing the task's **Verify** scenario (see Part 3)
 8. **Capture screenshots** — run test with `xvfb-run` and `--write-movie` to produce PNGs (see Screenshot Capture)
-9. **Verify visually** — read captured PNGs, compare to **Verify** description. If they don't match, identify the issue, fix scene/script/test, and repeat from step 3.
+9. **Verify visually** — read captured PNGs and check two things:
+   - **Task goal:** does the screenshot match the **Verify** description?
+   - **Visual quality & logic:** look for obvious bugs — geometry clipping through other geometry, objects floating in mid-air when they shouldn't be, wrong assets used (e.g., dog image where cat is expected), text overflow, UI elements overlapping or cut off at screen edges. Don't add decorations or polish beyond the task scope, but do fix clear correctness issues.
+   If either check fails, identify the issue, fix scene/script/test, and repeat from step 3.
 
 ## Iteration Tracking
 
PATCH

echo "Gold patch applied."
