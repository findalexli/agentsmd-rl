#!/usr/bin/env bash
set -euo pipefail

cd /workspace/auto-claude-code-research-in-sleep

# Idempotency guard
if grep -qF "Long-running refinement sessions may fail mid-way (e.g., API timeout, context co" "skills/research-refine/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/research-refine/SKILL.md b/skills/research-refine/SKILL.md
@@ -44,10 +44,43 @@ User input (PROBLEM + vague APPROACH)
 
 > Override via argument if needed, e.g. `/research-refine "problem | approach" -- max rounds: 3, threshold: 9`.
 
+## State Persistence (Checkpoint Recovery)
+
+Long-running refinement sessions may fail mid-way (e.g., API timeout, context compaction, or session interruption). To avoid losing completed work, persist state to `refine-logs/REFINE_STATE.json` after each phase boundary:
+
+```json
+{
+  "phase": "review",
+  "round": 1,
+  "threadId": "019cd392-...",
+  "last_score": 6.5,
+  "last_verdict": "REVISE",
+  "status": "in_progress",
+  "timestamp": "2026-03-22T20:00:00"
+}
+```
+
+**Field definitions:**
+
+| Field | Values | Meaning |
+|-------|--------|---------|
+| `phase` | `"anchor"` / `"proposal"` / `"review"` / `"refine"` / `"done"` | Last **completed** phase |
+| `round` | 0–MAX_ROUNDS | Current round number |
+| `threadId` | string or null | Reviewer thread ID for `codex-reply` continuity |
+| `last_score` | number or null | Most recent overall score from reviewer |
+| `last_verdict` | string or null | Most recent verdict (READY / REVISE / RETHINK) |
+| `status` | `"in_progress"` / `"completed"` | Loop status |
+| `timestamp` | ISO 8601 | When state was last written |
+
+**Write rules:**
+- **Write after each phase completes** (not before). Overwrite each time — only the latest state matters.
+- **On completion** (Phase 5 finished), set `"status": "completed"`.
+
 ## Output Structure
 
 ```
 refine-logs/
+├── REFINE_STATE.json
 ├── round-0-initial-proposal.md
 ├── round-1-review.md
 ├── round-1-refinement.md
@@ -64,6 +97,32 @@ Every `round-N-refinement.md` must contain a **full anchored proposal**, not jus
 
 ## Workflow
 
+### Initialization (Checkpoint Recovery)
+
+Before starting any phase, check whether a previous run left a checkpoint:
+
+1. **Check for `refine-logs/REFINE_STATE.json`**:
+   - If it **does not exist** → **fresh start** (proceed to Phase 0 normally)
+   - If it exists AND `status` is `"completed"` → **fresh start** (delete state file, previous run finished)
+   - If it exists AND `status` is `"in_progress"` AND `timestamp` is **older than 24 hours** → **fresh start** (stale state from a killed/abandoned run — delete the file)
+   - If it exists AND `status` is `"in_progress"` AND `timestamp` is **within 24 hours** → **resume**
+
+2. **On resume**, read the state file and recover context:
+   - Read all existing `refine-logs/round-*.md` files to restore prior work
+   - Read `refine-logs/score-history.md` if it exists
+   - Recover `threadId` for reviewer thread continuity
+   - Log to the user: `"Checkpoint found. Resuming after phase: {phase}, round: {round}."`
+   - **Jump to the next phase** based on the saved `phase` value:
+
+   | Saved `phase` | What was completed | Resume from |
+   |---------------|-------------------|-------------|
+   | `"anchor"` | Phase 0 done | Phase 1 (read anchor from round-0 context) |
+   | `"proposal"` | Phase 1 done | Phase 2 (read `round-0-initial-proposal.md`) |
+   | `"review"` | Phase 2 or 4 done | Phase 3 (read latest `round-N-review.md`) |
+   | `"refine"` | Phase 3 done | Phase 4 (read latest `round-N-refinement.md`) |
+
+3. **On fresh start**, ensure `refine-logs/` directory exists and proceed to Phase 0.
+
 ### Phase 0: Freeze the Problem Anchor
 
 Before proposing anything, extract the user's immutable bottom-line problem. This anchor must be copied verbatim into every proposal and every refinement round.
@@ -78,6 +137,8 @@ Write:
 
 If later reviewer feedback would change the problem being solved, mark that as **drift** and push back or adapt carefully.
 
+**Checkpoint:** Write `refine-logs/REFINE_STATE.json` with `{"phase": "anchor", "round": 0, "threadId": null, "last_score": null, "last_verdict": null, "status": "in_progress", "timestamp": "<now>"}`.
+
 ### Phase 1: Build the Initial Proposal
 
 #### Step 1.1: Scan Grounding Material
@@ -250,6 +311,8 @@ Use this structure:
 - Timeline:
 ```
 
+**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "proposal", "round": 0, ...}`.
+
 ### Phase 2: External Method Review (Round 1)
 
 Send the full proposal to GPT-5.4 for an **elegance-first, frontier-aware, method-first** review. The reviewer should spend most of the critique budget on the method itself, not on expanding the experiment menu.
@@ -325,6 +388,8 @@ mcp__codex__codex:
 
 Save review to `refine-logs/round-1-review.md` with the raw response in a `<details>` block.
 
+**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "review", "round": 1, "threadId": "<saved>", "last_score": <parsed>, "last_verdict": "<parsed>", ...}`.
+
 ### Phase 3: Parse Feedback and Revise the Method
 
 #### Step 3.1: Parse the Review
@@ -425,6 +490,8 @@ Save to `refine-logs/round-N-refinement.md`:
 [Full updated proposal from Problem Anchor through Claim-Driven Validation Sketch]
 ```
 
+**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "refine", "round": N, ...}`.
+
 ### Phase 4: Re-evaluation (Round 2+)
 
 Send the revised proposal back to GPT-5.4 in the **same thread**:
@@ -464,6 +531,8 @@ mcp__codex__codex-reply:
 
 Save review to `refine-logs/round-N-review.md`.
 
+**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "review", "round": N, "threadId": "<saved>", "last_score": <parsed>, "last_verdict": "<parsed>", ...}`.
+
 Then return to Phase 3 until:
 
 - **Overall score >= SCORE_THRESHOLD** and verdict is READY and no unresolved drift
@@ -621,6 +690,8 @@ Final proposal: refine-logs/FINAL_PROPOSAL.md
 Suggested next step: /experiment-plan
 ```
 
+**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "done", "status": "completed", ...}`.
+
 ## Key Rules
 
 - **Large file handling**: If the Write tool fails due to file size, immediately retry using Bash (`cat << 'EOF' > file`) to write in chunks. Do NOT ask the user for permission — just do it silently.
PATCH

echo "Gold patch applied."
