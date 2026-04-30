#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ouroboros

# Idempotency guard
if grep -qF "- **REJECTED at Stage 1** (mechanical): `\ud83d\udccd Next: Fix the build/test failures abo" "skills/evaluate/SKILL.md" && grep -qF "- `stagnated`: `\ud83d\udccd Next: ooo unstuck to break through, then ooo evolve --status <" "skills/evolve/SKILL.md" && grep -qF "`\ud83d\udccd Next: ooo seed to crystallize these requirements into a specification`" "skills/interview/SKILL.md" && grep -qF "- **Max iterations reached**: `\ud83d\udccd Next: ooo interview to re-examine the problem \u2014" "skills/ralph/SKILL.md" && grep -qF "- **REVISE**: Show differences/suggestions, then `\ud83d\udccd Next: Fix the issues above, " "skills/run/SKILL.md" && grep -qF "\ud83d\udccd Next: `ooo run` to execute this seed (requires `ooo setup` first)" "skills/seed/SKILL.md" && grep -qF "- Drift > 0.3: `\ud83d\udccd Warning: significant drift detected. Consider ooo interview to" "skills/status/SKILL.md" && grep -qF "\ud83d\udccd Next: Try the approach above, then `ooo run` to execute \u2014 or `ooo interview` t" "skills/unstuck/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/evaluate/SKILL.md b/skills/evaluate/SKILL.md
@@ -65,6 +65,11 @@ When the user invokes this skill:
    - Highlight the final approval decision
    - If rejected, explain the failure reason
    - Suggest fixes if evaluation fails
+   - Always end with a 📍 suggestion based on the outcome:
+     - **APPROVED**: `📍 Done! Your implementation passes all checks. Optional: ooo evolve to iteratively refine`
+     - **REJECTED at Stage 1** (mechanical): `📍 Next: Fix the build/test failures above, then ooo evaluate — or ooo ralph for automated fix loop`
+     - **REJECTED at Stage 2** (semantic): `📍 Next: ooo run to re-execute with fixes — or ooo evolve for iterative refinement`
+     - **REJECTED at Stage 3** (consensus): `📍 Next: ooo interview to re-examine requirements — or ooo unstuck to challenge assumptions`
 
 ## Fallback (No MCP Server)
 
@@ -94,4 +99,6 @@ Stage 2: Semantic Evaluation
   AC Compliance: YES
   Goal Alignment: 0.90
   Drift Score: 0.08
+
+📍 Done! Your implementation passes all checks. Optional: `ooo evolve` to iteratively refine
 ```
diff --git a/skills/evolve/SKILL.md b/skills/evolve/SKILL.md
@@ -60,6 +60,11 @@ ooo evolve --rewind <lineage_id> <generation_number>
    - `exhausted` → Max 30 generations reached. Display best result
    - `failed` → Check error, possibly retry
 7. **Repeat step 6** until action ≠ `continue`
+8. When the loop terminates, display a result summary with next step:
+   - `converged`: `📍 Next: Ontology converged! Run ooo evaluate for formal verification`
+   - `stagnated`: `📍 Next: ooo unstuck to break through, then ooo evolve --status <lineage_id> to resume`
+   - `exhausted`: `📍 Next: ooo evaluate to check best result — or ooo unstuck to try a new approach`
+   - `failed`: `📍 Next: Check the error above. ooo status to inspect session, or ooo unstuck if blocked`
 
 **Checking status:**
 1. Call `ouroboros_lineage_status` with the `lineage_id`
diff --git a/skills/interview/SKILL.md b/skills/interview/SKILL.md
@@ -65,7 +65,8 @@ If the `ouroboros_interview` MCP tool is available, use it for persistent, struc
 
 4. **Repeat steps 2-3** until the user says "done" or requirements are clear.
 
-5. After completion, suggest `ooo seed` to generate the Seed specification.
+5. After completion, suggest the next step in `📍 Next:` format:
+   `📍 Next: ooo seed to crystallize these requirements into a specification`
 
 **Advantages of MCP mode**: State persists to disk (survives session restarts), ambiguity scoring, direct integration with `ooo seed` via session ID, structured input with AskUserQuestion.
 
@@ -79,6 +80,8 @@ If the MCP tool is NOT available, fall back to agent-based interview:
 4. Use Read, Glob, Grep, WebFetch to explore context if needed
 5. Continue until the user says "done"
 6. Interview results live in conversation context (not persisted)
+7. After completion, suggest the next step in `📍 Next:` format:
+   `📍 Next: ooo seed to crystallize these requirements into a specification`
 
 ## Interviewer Behavior (Both Modes)
 
@@ -101,6 +104,8 @@ User: Create, read, update, delete
 Q3: Will tasks have relationships (e.g., subtasks, tags)?
 User: Yes, tags for organizing
 
+📍 Next: `ooo seed` to crystallize these requirements into a specification
+
 User: ooo seed  [Generate seed from interview]
 ```
 
diff --git a/skills/ralph/SKILL.md b/skills/ralph/SKILL.md
@@ -96,7 +96,11 @@ When the user invokes this skill:
            break
    ```
 
-4. **Report progress** each iteration:
+4. **On termination**, display a 📍 next-step:
+   - **Success** (QA passed): `📍 Next: ooo evaluate for formal 3-stage verification`
+   - **Max iterations reached**: `📍 Next: ooo interview to re-examine the problem — or ooo unstuck to try a different approach`
+
+5. **Report progress** each iteration:
    ```
    [Ralph Iteration <i>/<max>]
    Execution complete. Running QA...
@@ -112,7 +116,7 @@ When the user invokes this skill:
    The boulder never stops. Continuing...
    ```
 
-5. **Handle interruption**:
+6. **Handle interruption**:
    - If user says "stop": save checkpoint, exit gracefully
    - If user says "continue": reload from last checkpoint
    - State persists across session resets
@@ -186,6 +190,8 @@ QA History:
 - Iteration 3: PASS (1.0)
 
 All tests passing. Build successful.
+
+📍 Next: `ooo evaluate` for formal 3-stage verification
 ```
 
 ## Cancellation
diff --git a/skills/run/SKILL.md b/skills/run/SKILL.md
@@ -59,10 +59,10 @@ When the user invokes this skill:
    The QA verdict is included in the tool response text.
    To skip: pass `skip_qa: true` to the tool.
 
-   Present QA verdict from the response:
-   - **PASS**: suggest `ooo evaluate` for formal evaluation
-   - **REVISE**: show differences/suggestions, offer to re-run
-   - **FAIL/ESCALATE**: surface to user for manual review
+   Present QA verdict with next step:
+   - **PASS**: `📍 Next: ooo evaluate <session_id> for formal 3-stage verification`
+   - **REVISE**: Show differences/suggestions, then `📍 Next: Fix the issues above, then ooo run to retry — or ooo unstuck if blocked`
+   - **FAIL/ESCALATE**: `📍 Next: Review failures above, then ooo run to retry — or ooo unstuck if blocked`
 
 ## Fallback (No MCP Server)
 
@@ -93,5 +93,5 @@ Result:
   Duration: 45.2s
   Messages Processed: 12
 
-  Next: /ouroboros:evaluate sess-abc-123
+  📍 Next: `ooo evaluate sess-abc-123` for formal 3-stage verification
 ```
diff --git a/skills/seed/SKILL.md b/skills/seed/SKILL.md
@@ -126,5 +126,6 @@ Create `~/.ouroboros/` directory if it doesn't exist.
 If `star_asked` is already `true`, skip the question and just announce:
 
 ```
-Your seed has been crystallized! Run `ooo run` to execute (requires `ooo setup` first).
+Your seed has been crystallized!
+📍 Next: `ooo run` to execute this seed (requires `ooo setup` first)
 ```
diff --git a/skills/status/SKILL.md b/skills/status/SKILL.md
@@ -52,6 +52,10 @@ When the user invokes this skill:
    - Show progress information
    - If drift measured, show the drift report
    - If drift exceeds threshold (0.3), warn and suggest actions
+   - End with a `📍` next-step based on context:
+     - No drift measured: `📍 Session active — say "am I drifting?" to measure drift, or continue with ooo run`
+     - Drift ≤ 0.3: `📍 On track — continue with ooo run or ooo evaluate when ready`
+     - Drift > 0.3: `📍 Warning: significant drift detected. Consider ooo interview to re-clarify, or ooo evolve to course-correct`
 
 ## Drift Thresholds
 
@@ -94,4 +98,6 @@ Component Breakdown:
   Ontology Drift: 0.20 (20% weight)
 
 You're on track. Goal alignment is strong.
+
+📍 On track — continue with `ooo run` or `ooo evaluate` when ready
 ```
diff --git a/skills/unstuck/SKILL.md b/skills/unstuck/SKILL.md
@@ -55,7 +55,7 @@ When the user invokes this skill:
    - Show the persona's approach summary
    - Present the reframing prompt
    - List the questions to consider
-   - Suggest concrete next steps
+   - Suggest concrete next steps with a `📍 Next:` action routing back to the workflow
 
 ## Fallback (No MCP Server)
 
@@ -85,4 +85,6 @@ with 2 tables, you haven't found the core feature yet.
 - What is the ONE query your users will run most?
 - Can you use a single JSON column instead of normalized tables?
 - What if you started with flat files and added a DB later?
+
+📍 Next: Try the approach above, then `ooo run` to execute — or `ooo interview` to re-examine the problem
 ```
PATCH

echo "Gold patch applied."
