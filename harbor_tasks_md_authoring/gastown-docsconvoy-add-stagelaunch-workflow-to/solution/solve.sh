#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gastown

# Idempotency guard
if grep -qF "description: The definitive guide for working with gastown's convoy system -- ba" "docs/skills/convoy/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/skills/convoy/SKILL.md b/docs/skills/convoy/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: convoy
-description: The definitive guide for working with gastown's convoy system -- batch work tracking, event-driven feeding, and dispatch safety guards. Use when writing convoy code, debugging convoy behavior, adding convoy features, testing convoy changes, or answering questions about how convoys work. Triggers on convoy, convoy manager, convoy feeding, dispatch, stranded convoy, feedFirstReady, feedNextReadyIssue, IsSlingableType, isIssueBlocked, CheckConvoysForIssue, gt convoy, gt sling.
+description: The definitive guide for working with gastown's convoy system -- batch work tracking, event-driven feeding, stage-launch workflow, and dispatch safety guards. Use when writing convoy code, debugging convoy behavior, adding convoy features, testing convoy changes, or answering questions about how convoys work. Triggers on convoy, convoy manager, convoy feeding, dispatch, stranded convoy, feedFirstReady, feedNextReadyIssue, IsSlingableType, isIssueBlocked, CheckConvoysForIssue, gt convoy, gt sling, stage, launch, staged, wave.
 ---
 
 # Gastown Convoy System
@@ -10,18 +10,29 @@ The convoy system tracks batches of work across rigs. A convoy is a bead that `t
 ## Architecture
 
 ```
-+========================= CREATION ==========================+
-|                                                              |
-|   gt sling <beads>          gt convoy create <name> ...      |
-|        |  (auto-convoy)          |  (explicit convoy)        |
-|        v                         v                           |
-|   +--------------------------------------------------+       |
-|   |            CONVOY (hq-cv-*)                      |       |
-|   |        tracks: issue1, issue2, ...               |       |
-|   |        status: open / closed                     |       |
-|   +--------------------------------------------------+       |
-|                                                              |
-+==============================================================+
++================================ CREATION =================================+
+|                                                                            |
+|   gt sling <beads>      gt convoy create ...     gt convoy stage <epic>    |
+|        |  (auto-convoy)       |  (explicit)            |  (validated)     |
+|        v                      v                        v                  |
+|   +-----------+          +-----------+         +----------------+         |
+|   |  status:  |          |  status:  |         |    status:     |         |
+|   |   open    |          |   open    |         | staged:ready   |         |
+|   +-----------+          +-----------+         | staged:warnings|         |
+|                                                +----------------+         |
+|                                                        |                  |
+|                                              gt convoy launch             |
+|                                                        |                  |
+|                                                        v                  |
+|                                                +----------------+         |
+|                                                |    status:     |         |
+|                                                |     open       |         |
+|                                                | (Wave 1 slung) |         |
+|                                                +----------------+         |
+|                                                                            |
+|   All paths produce: CONVOY (hq-cv-*)                                      |
+|                      tracks: issue1, issue2, ...                           |
++============================================================================+
               |                              |
               v                              v
 += EVENT-DRIVEN FEEDER (5s) =+   +=== STRANDED SCAN (30s) ===+
@@ -44,9 +55,9 @@ The convoy system tracks batches of work across rigs. A convoy is a bead that `t
 +==============================+
 ```
 
-Two feed paths, same safety guards:
-- **Event-driven** (`operations.go`): Polls beads stores every ~5s for close events. Calls `feedNextReadyIssue` which checks `IsSlingableType` + `isIssueBlocked` before dispatch.
-- **Stranded scan** (`convoy_manager.go`): Runs every 30s. `feedFirstReady` iterates all ready issues. The ready list is pre-filtered by `IsSlingableType` in `findStrandedConvoys` (cmd/convoy.go).
+Three creation paths (sling, create, stage), two feed paths, same safety guards:
+- **Event-driven** (`operations.go`): Polls beads stores every ~5s for close events. Calls `feedNextReadyIssue` which checks `IsSlingableType` + `isIssueBlocked` before dispatch. **Skips staged convoys** (`isConvoyStaged` check).
+- **Stranded scan** (`convoy_manager.go`): Runs every 30s. `feedFirstReady` iterates all ready issues. The ready list is pre-filtered by `IsSlingableType` in `findStrandedConvoys` (cmd/convoy.go). **Only sees open convoys** — staged convoys never appear.
 
 ## Safety guards (the three rules)
 
@@ -79,6 +90,18 @@ Both feed paths iterate past failures instead of giving up:
 
 ## CLI commands
 
+### Stage and launch (validated creation)
+
+```bash
+gt convoy stage <epic-id>            # analyze deps, build DAG, compute waves, create staged convoy
+gt convoy stage gt-task1 gt-task2    # stage from explicit task list
+gt convoy stage hq-cv-abc            # re-stage existing staged convoy
+gt convoy stage <epic-id> --json     # machine-readable output
+gt convoy stage <epic-id> --launch   # stage + immediately launch if no errors
+gt convoy launch hq-cv-abc           # transition staged → open, dispatch Wave 1
+gt convoy launch <epic-id>           # stage + launch in one step (delegates to stage --launch)
+```
+
 ### Create and manage
 
 ```bash
@@ -145,6 +168,146 @@ gt sling gt-task1 gt-task2 gt-task3 gastown
 # -> Created convoy hq-cv-xxxxx tracking 3 beads
 ```
 
+## Stage-launch workflow
+
+> Implemented in [PR #1820](https://github.com/steveyegge/gastown/pull/1820). Depends on the feeder safety guards from [PR #1759](https://github.com/steveyegge/gastown/pull/1759). Design docs: `docs/design/convoy/stage-launch/prd.md`, `docs/design/convoy/stage-launch/testing.md`.
+
+The stage-launch workflow is a two-phase convoy creation path that validates dependencies and computes wave dispatch order **before** any work is dispatched. This is the preferred path for epic delivery.
+
+### Input types
+
+`gt convoy stage` accepts three mutually exclusive input types:
+
+| Input | Example | Behavior |
+|-------|---------|----------|
+| Epic ID | `gt convoy stage bcc-nxk2o` | BFS walks entire parent-child tree, collects all descendants |
+| Task list | `gt convoy stage gt-t1 gt-t2 gt-t3` | Analyzes exactly those tasks |
+| Convoy ID | `gt convoy stage hq-cv-abc` | Re-reads tracked beads from existing staged convoy (re-stage) |
+
+Mixed types (e.g., epic + task together) error. Multiple epics or multiple convoys error.
+
+### Processing pipeline
+
+```
+1. validateStageArgs     — reject empty/flag-like args
+2. bdShow each arg       — resolve bead types
+3. resolveInputKind      — classify Epic / Tasks / Convoy
+4. collectBeads          — gather BeadInfo + DepInfo (BFS for epic, direct for tasks)
+5. buildConvoyDAG        — construct in-memory DAG (nodes + edges)
+6. detectErrors          — cycle detection + missing rig checks
+7. detectWarnings        — orphans, parked rigs, cross-rig, capacity, missing branches
+8. categorizeFindings    — split into errors / warnings
+9. chooseStatus          — staged:ready, staged:warnings, or abort on errors
+10. computeWaves         — Kahn's algorithm (only when no errors)
+11. renderDAGTree        — print ASCII dependency tree
+12. renderWaveTable      — print wave dispatch plan
+13. createStagedConvoy   — bd create --type=convoy --status=<staged-status>
+```
+
+### Wave computation (Kahn's algorithm)
+
+Only slingable types participate in waves: `task`, `bug`, `feature`, `chore`. Epics are excluded.
+
+Execution edges (create wave ordering):
+- `blocks`
+- `conditional-blocks`
+- `waits-for`
+
+Non-execution edges (ignored for wave ordering):
+- `parent-child` — hierarchy only
+- `related`, `tracks`, `discovered-from`
+
+**Algorithm:**
+1. Filter to slingable nodes only
+2. Calculate in-degree for each node (count BlockedBy edges to other slingable nodes)
+3. Peel loop: collect all nodes with in-degree 0 → Wave N; remove them; decrement neighbors; repeat
+4. Sort within each wave alphabetically for determinism
+
+Output example:
+```
+  Wave   ID              Title                     Rig       Blocked By
+  ──────────────────────────────────────────────────────────────────────
+  1      bcc-nxk2o.1.1   Init scaffolding          bcc       —
+  2      bcc-nxk2o.1.2   Shared types              bcc       bcc-nxk2o.1.1
+  3      bcc-nxk2o.1.3   CLI wrapper               bcc       bcc-nxk2o.1.2
+
+  3 tasks across 3 waves (max parallelism: 1 in wave 1)
+```
+
+### Convoy status model
+
+Four statuses with defined transitions:
+
+| Status | Meaning |
+|--------|---------|
+| `staged:ready` | Validated, no errors or warnings, ready to launch |
+| `staged:warnings` | Validated, no errors but has warnings. Fix and re-stage, or launch anyway. |
+| `open` | Active — daemon feeds work as beads close |
+| `closed` | Complete or cancelled |
+
+Valid transitions:
+
+| From → To | Allowed? |
+|-----------|----------|
+| `staged:ready` → `open` | Yes (launch) |
+| `staged:warnings` → `open` | Yes (launch) |
+| `staged:*` → `closed` | Yes (cancel) |
+| `staged:ready` ↔ `staged:warnings` | Yes (re-stage) |
+| `open` → `closed` | Yes |
+| `closed` → `open` | Yes (reopen) |
+| `open` → `staged:*` | **No** |
+| `closed` → `staged:*` | **No** |
+
+### Error vs warning classification
+
+**Errors** (fatal — prevent convoy creation):
+
+| Category | Trigger | Fix |
+|----------|---------|-----|
+| `cycle` | Cycle detected in execution edges | Remove one blocking dep in the cycle |
+| `no-rig` | Slingable bead has no rig (prefix not in routes.jsonl) | Add routes.jsonl entry |
+
+**Warnings** (non-fatal — convoy created as `staged:warnings`):
+
+| Category | Trigger |
+|----------|---------|
+| `orphan` | Slingable task with no blocking deps in either direction (epic input only) |
+| `parked-rig` | Bead's rig name contains "parked" (case-insensitive) |
+| `cross-rig` | Bead on a different rig than the majority |
+| `capacity` | A wave has more than 5 tasks |
+| `missing-branch` | Sub-epic with children but no integration branch |
+
+### Launch behavior
+
+`gt convoy launch <convoy-id>` transitions a staged convoy to open and dispatches Wave 1:
+
+1. Validate convoy exists and is staged
+2. Transition status to `open`
+3. Re-read tracked beads, rebuild DAG, recompute waves
+5. Dispatch every task in Wave 1 via `gt sling <beadID> <rig>`
+6. Individual sling failures do NOT abort remaining dispatches
+7. Print dispatch results (checkmark/X per task)
+8. Subsequent waves handled automatically by the daemon
+
+If `gt convoy launch` receives an epic or task list (not a staged convoy), it delegates to `gt convoy stage --launch` to stage-then-launch in one step.
+
+### Staged convoy daemon safety
+
+**Staged convoys are completely inert to the daemon.** Neither feed path processes them:
+
+- **Event-driven feeder:** `isConvoyStaged` check in `CheckConvoysForIssue` skips any convoy with `staged:*` status. Fail-open on read errors (assumes not staged → processes, which is safe since a read error on a non-existent convoy does nothing).
+- **Stranded scan:** `gt convoy stranded` only returns open convoys. Staged convoys never appear.
+
+This means you can stage a convoy, review the wave plan, and launch when ready — no risk of premature dispatch.
+
+### Re-staging
+
+Running `gt convoy stage <convoy-id>` on an existing staged convoy re-analyzes and updates:
+- Re-reads tracked beads from the convoy's `tracks` deps
+- Rebuilds DAG, re-detects errors/warnings, recomputes waves
+- Updates status via `bd update` (e.g., `staged:warnings` → `staged:ready` if warnings resolved)
+- Does NOT create a new convoy or re-add track dependencies
+
 ## Testing convoy changes
 
 ### Running tests
@@ -161,6 +324,13 @@ go test ./internal/cmd/... -v -count=1 -run TestCreateBatchConvoy  # batch sling
 go test ./internal/cmd/... -v -count=1 -run TestBatchSling
 go test ./internal/cmd/... -v -count=1 -run TestResolveRig      # rig resolution
 go test ./internal/daemon/... -v -count=1 -run Integration      # real beads stores
+
+# Stage-launch:
+go test ./internal/cmd/... -v -count=1 -run TestConvoyStage     # staging logic
+go test ./internal/cmd/... -v -count=1 -run TestConvoyLaunch    # launch + Wave 1 dispatch
+go test ./internal/cmd/... -v -count=1 -run TestDetectCycles    # cycle detection
+go test ./internal/cmd/... -v -count=1 -run TestComputeWaves    # wave computation
+go test ./internal/cmd/... -v -count=1 -run TestBuildConvoyDAG  # DAG construction
 ```
 
 ### Key test invariants
@@ -176,10 +346,20 @@ go test ./internal/daemon/... -v -count=1 -run Integration      # real beads sto
 - `parent-child` deps are NOT blocking
 - Batch sling creates exactly 1 convoy for N beads (not N convoys)
 - `resolveRigFromBeadIDs` errors on mixed prefixes, unmapped prefixes, town-level prefixes
+- Cycles in blocking deps prevent staged convoy creation (exit non-zero, no side effects)
+- Wave 1 contains ONLY tasks with zero unsatisfied blocking deps among slingable nodes
+- Epics and non-slingable types are NEVER placed in waves
+- Daemon does NOT feed issues from `staged:*` convoys (both feed paths skip)
+- `staged:warnings` convoys can still be launched (warnings are informational)
+- Re-staging a convoy does NOT create duplicates (updates in place)
+- Launch dispatches ONLY Wave 1, not subsequent waves
+- Wave computation is deterministic (same input → same output, alphabetical sort within waves)
 
 ### Deeper test engineering
 
-See `docs/design/convoy/testing.md` for the full test plan covering failure modes, coverage gaps, harness scorecard, test matrix, and recommended test strategy.
+See `docs/design/convoy/stage-launch/testing.md` for the full stage-launch test plan (105 tests across unit, integration, snapshot, and property tiers).
+
+See `docs/design/convoy/testing.md` for the general convoy test plan covering failure modes, coverage gaps, harness scorecard, test matrix, and recommended test strategy.
 
 ## Common pitfalls
 
@@ -189,6 +369,11 @@ See `docs/design/convoy/testing.md` for the full test plan covering failure mode
 - **Empty IssueType is slingable.** Beads default to type "task" when IssueType is unset. Treating empty as non-slingable would break all legacy beads.
 - **`isIssueBlocked` is fail-open.** Store errors assume not blocked. A transient Dolt error should not permanently stall a convoy -- the next feed cycle retries with fresh state.
 - **Explicit rig in batch sling is deprecated.** `gt sling beads... rig` still works but prints a warning. Prefer `gt sling beads...` with auto-resolution.
+- **Staged convoys are inert.** The daemon ignores them completely. Don't expect auto-feeding until you `gt convoy launch`.
+- **Review `staged:warnings` before launching.** Warnings are informational — fix and re-stage if possible, or launch anyway if they're acceptable.
+- **`gt convoy launch` on a non-staged input delegates to stage.** If you pass an epic or task list to `launch`, it runs `stage --launch` internally. Only an already-staged convoy gets the fast path.
+- **Wave computation is informational.** Waves are computed at stage time for display. Runtime dispatch uses the daemon's per-cycle `isIssueBlocked` checks, which are more dynamic.
+- **You cannot un-stage an open convoy.** Once launched, a convoy cannot return to staged status. The `open → staged:*` transition is rejected.
 
 ## Key source files
 
@@ -200,4 +385,6 @@ See `docs/design/convoy/testing.md` for the full test plan covering failure mode
 | `internal/cmd/sling.go` | Batch detection at ~242, auto-rig-resolution, deprecation warning |
 | `internal/cmd/sling_batch.go` | `runBatchSling`, `resolveRigFromBeadIDs`, `allBeadIDs`, cross-rig guard |
 | `internal/cmd/sling_convoy.go` | `createAutoConvoy`, `createBatchConvoy`, `printConvoyConflict` |
+| `internal/cmd/convoy_stage.go` | `gt convoy stage`: DAG walking, wave computation, error/warning detection, staged convoy creation |
+| `internal/cmd/convoy_launch.go` | `gt convoy launch`: status transition, Wave 1 dispatch via `dispatchWave1` |
 | `internal/daemon/daemon.go` | Daemon startup -- creates `ConvoyManager` at ~237 |
PATCH

echo "Gold patch applied."
