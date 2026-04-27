#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ouroboros

# Idempotency guard
if grep -qF "description: \"Check once when each parallel level completes. Most context-effici" "skills/run/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/run/SKILL.md b/skills/run/SKILL.md
@@ -72,15 +72,65 @@ The Ouroboros MCP tools are often registered as **deferred tools** that must be
      session_id: <existing session ID>
    ```
 
-5. **Poll for progress** using `ouroboros_job_wait`:
+5. **Ask user about polling strategy** using `AskUserQuestion` immediately after IDs are returned:
+
+   Present the session/job IDs first, then ask:
+
+   ```
+   Question: "Execution started. How would you like to monitor progress?"
+   Header: "Monitoring"
+   Options:
+     - label: "Poll here (Recommended)"
+       description: "Poll in this session. Context window is consumed but you get real-time updates."
+     - label: "Don't poll — I'll monitor separately"
+       description: "End here. Use `ooo status <session_id>` in a new terminal or /clone to monitor."
+   ```
+
+   **If user chooses "Poll here"**, ask follow-up:
+   ```
+   Question: "How often should I check progress?"
+   Header: "Interval"
+   Options:
+     - label: "Per level (Recommended)"
+       description: "Check once when each parallel level completes. Most context-efficient with meaningful updates."
+     - label: "Every 10 minutes"
+       description: "Periodic check regardless of level progress. Balanced context usage."
+     - label: "Every 20 minutes"
+       description: "Minimal context usage. Best for large seeds with many ACs."
+   ```
+
+   Then display:
+   ```
+   💡 Note: Context compression may occur during long executions.
+   MCP tools remain available after compression, but prior poll results are summarized.
+   If this session is needed for follow-up (ooo evaluate, ooo evolve), shorter polling = more context consumed.
+   ```
+
+   **If user chooses "Don't poll"**, display:
+
+   ```
+   Execution running in background.
+   Session ID: <session_id>
+   Job ID: <job_id>
+   
+   To monitor progress:
+     Option A: Open a new terminal → `ooo status <session_id>`
+     Option B: Use /clone to fork this conversation for monitoring
+     Option C: Come back later and run `ooo status <session_id>` here
+   
+   When execution completes, continue with: `ooo evaluate <session_id>`
+   ```
+   Then **stop** — do NOT proceed to polling steps.
+
+6. **Poll for progress** using `ouroboros_job_wait` (only if user chose to poll):
    ```
    loop:
      Tool: ouroboros_job_wait
      Arguments:
        job_id: <job_id from step 3>
        cursor: <cursor from previous response, starts at 0>
        timeout_seconds: 60
-
+   
      # Returns immediately when state changes; waits up to 60s otherwise.
      # This reduces tool call round-trips and context consumption.
      # Continue until status is "completed", "failed", or "cancelled"
@@ -91,19 +141,19 @@ The Ouroboros MCP tools are often registered as **deferred tools** that must be
    [Executing] Phase: <current_phase> | AC: <completed>/<total>
    ```
 
-6. **Fetch final result** with `ouroboros_job_result`:
+7. **Fetch final result** with `ouroboros_job_result`:
    ```
    Tool: ouroboros_job_result
    Arguments:
      job_id: <job_id>
    ```
 
-7. Present the execution results to the user:
+8. Present the execution results to the user:
    - Show success/failure status
    - Show session ID (for later status checks)
    - Show execution summary
 
-8. **Post-execution QA** (automatic):
+9. **Post-execution QA** (automatic):
    `ouroboros_start_execute_seed` automatically runs QA after successful execution.
    The QA verdict is included in the final job result text.
    To skip: pass `skip_qa: true` to the tool.
PATCH

echo "Gold patch applied."
