#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "If a task shows `upstream_failed`, the root cause is in an upstream task. Use `a" "skills/testing-dags/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/testing-dags/SKILL.md b/skills/testing-dags/SKILL.md
@@ -5,61 +5,36 @@ description: Complex DAG testing workflows with debugging and fixing cycles. Use
 
 # DAG Testing Skill
 
----
+Use `af` commands to test, debug, and fix DAGs in iterative cycles.
 
-## 🚀 FIRST ACTION: Just Trigger the DAG
+## Running the CLI
 
-When the user asks to test a DAG, your **FIRST AND ONLY action** should be:
+Run all `af` commands using uvx (no installation required):
 
+```bash
+uvx --from astro-airflow-mcp@latest af <command>
 ```
-trigger_dag_and_wait(dag_id="<dag_id>", timeout=300)
-```
-
-**DO NOT:**
-- ❌ Call `list_dags` first
-- ❌ Call `get_dag_details` first
-- ❌ Call `list_import_errors` first
-- ❌ Use `grep` or `ls` or any bash command
-- ❌ Do any "pre-flight checks"
 
-**Just trigger the DAG.** If it fails, THEN debug.
+Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp@latest af`.
 
 ---
 
-## ⚠️ CRITICAL WARNING: Use MCP Tools, NOT CLI Commands ⚠️
+## FIRST ACTION: Just Trigger the DAG
 
-> **STOP! Before running ANY Airflow-related command, read this.**
->
-> You MUST use MCP tools for ALL Airflow interactions. CLI commands like `astro dev run`, `airflow dags test`, or shell commands to read logs are **FORBIDDEN**.
->
-> **Why?** MCP tools provide structured, reliable output. CLI commands are fragile, produce unstructured text, and often fail silently.
+When the user asks to test a DAG, your **FIRST AND ONLY action** should be:
 
----
+```bash
+af runs trigger-wait <dag_id>
+```
+
+**DO NOT:**
+- Call `af dags list` first
+- Call `af dags get` first
+- Call `af dags errors` first
+- Use `grep` or `ls` or any other bash command
+- Do any "pre-flight checks"
 
-## CLI vs MCP Quick Reference
-
-| ❌ DO NOT USE | ✅ USE INSTEAD |
-|---------------|----------------|
-| `astro dev run dags test` | `trigger_dag_and_wait` MCP tool |
-| `airflow dags test` | `trigger_dag_and_wait` MCP tool |
-| `airflow tasks test` | `trigger_dag_and_wait` MCP tool |
-| `cat` / `grep` / `tail` on logs | `get_task_logs` MCP tool |
-| `astro dev run dags list` | `list_dags` MCP tool |
-| Any `astro dev run ...` | Equivalent MCP tool |
-| Any `airflow ...` CLI | Equivalent MCP tool |
-| `ls` on `/usr/local/airflow/dags/` | `list_dags` or `explore_dag` MCP tool |
-| `cat ... \| jq` to filter MCP results | Read the JSON directly from MCP response |
-| `grep` on MCP tool result files | Read the JSON directly from MCP response |
-| `ls` on local dags directory | Not needed — just trigger the DAG |
-| `pwd` to check directory | Not needed — just trigger the DAG |
-
-**Remember:**
-- ✅ Airflow is ALREADY running — the MCP server handles the connection
-- ✅ Just call `trigger_dag_and_wait` — don't check anything first
-- ❌ Do NOT call `list_dags` before testing — just trigger
-- ❌ Do NOT use shell commands (`ls`, `grep`, `cat`, `pwd`)
-- ❌ Do NOT use bash to parse or filter MCP tool results
-- ❌ Do NOT do "pre-flight checks" — try first, debug on failure
+**Just trigger the DAG.** If it fails, THEN debug.
 
 ---
 
@@ -95,22 +70,22 @@ trigger_dag_and_wait(dag_id="<dag_id>", timeout=300)
 
 ## Phase 1: Trigger and Wait
 
-Use `trigger_dag_and_wait` to test the DAG:
+Use `af runs trigger-wait` to test the DAG:
 
 ### Primary Method: Trigger and Wait
 
-**MCP tool:** `trigger_dag_and_wait(dag_id="your_dag_id", timeout=300)`
-
+```bash
+af runs trigger-wait <dag_id> --timeout 300
 ```
-trigger_dag_and_wait(
-    dag_id="my_dag",
-    conf={},           # Optional: pass config to the DAG
-    timeout=300        # Wait up to 5 minutes (adjust as needed)
-)
+
+**Example:**
+
+```bash
+af runs trigger-wait my_dag --timeout 300
 ```
 
 **Why this is the preferred method:**
-- Single tool call handles trigger + monitoring
+- Single command handles trigger + monitoring
 - Returns immediately when DAG completes (success or failure)
 - Includes failed task details if run fails
 - No manual polling required
@@ -166,13 +141,13 @@ trigger_dag_and_wait(
 
 Use this only when you need more control:
 
-```
+```bash
 # Step 1: Trigger
-trigger_dag(dag_id="my_dag", conf={})
+af runs trigger my_dag
 # Returns: {"dag_run_id": "manual__...", "state": "queued"}
 
 # Step 2: Check status
-get_dag_run(dag_id="my_dag", dag_run_id="manual__...")
+af runs get my_dag manual__2025-01-14T...
 # Returns current state
 ```
 
@@ -192,7 +167,7 @@ The DAG ran successfully. Summarize for the user:
 ### If Timed Out
 
 The DAG is still running. Options:
-1. Check current status with `get_dag_run(dag_id, dag_run_id)`
+1. Check current status: `af runs get <dag_id> <dag_run_id>`
 2. Ask user if they want to continue waiting
 3. Increase timeout and try again
 
@@ -204,11 +179,13 @@ Move to Phase 2 (Debug) to identify the root cause.
 
 ## Phase 2: Debug Failures (Only If Needed)
 
-When a DAG run fails, use these tools to diagnose:
+When a DAG run fails, use these commands to diagnose:
 
 ### Get Comprehensive Diagnosis
 
-**MCP tool:** `diagnose_dag_run(dag_id, dag_run_id)`
+```bash
+af runs diagnose <dag_id> <dag_run_id>
+```
 
 Returns in one call:
 - Run metadata (state, timing)
@@ -218,15 +195,20 @@ Returns in one call:
 
 ### Get Task Logs
 
-**MCP tool:** `get_task_logs(dag_id, dag_run_id, task_id)`
+```bash
+af tasks logs <dag_id> <dag_run_id> <task_id>
+```
 
+**Example:**
+
+```bash
+af tasks logs my_dag manual__2025-01-14T... extract_data
 ```
-get_task_logs(
-    dag_id="my_dag",
-    dag_run_id="manual__2025-01-14T...",
-    task_id="extract_data",
-    try_number=1        # Which attempt (1 = first try)
-)
+
+**For specific retry attempt:**
+
+```bash
+af tasks logs my_dag manual__2025-01-14T... extract_data --try 2
 ```
 
 **Look for:**
@@ -238,13 +220,15 @@ get_task_logs(
 
 ### Check Upstream Tasks
 
-If a task shows `upstream_failed`, the root cause is in an upstream task. Use `diagnose_dag_run` to find which task actually failed.
+If a task shows `upstream_failed`, the root cause is in an upstream task. Use `af runs diagnose` to find which task actually failed.
 
 ### Check Import Errors (If DAG Didn't Run)
 
 If the trigger failed because the DAG doesn't exist:
 
-**MCP tool:** `list_import_errors`
+```bash
+af dags errors
+```
 
 This reveals syntax errors or missing dependencies that prevented the DAG from loading.
 
@@ -260,88 +244,110 @@ Once you identify the issue:
 |-------|-----|
 | Missing import | Add to DAG file |
 | Missing package | Add to `requirements.txt` |
-| Connection error | Check `list_connections`, verify credentials |
-| Variable missing | Check `list_variables`, create if needed |
+| Connection error | Check `af config connections`, verify credentials |
+| Variable missing | Check `af config variables`, create if needed |
 | Timeout | Increase task timeout or optimize query |
 | Permission error | Check credentials in connection |
 
 ### After Fixing
 
 1. Save the file
-2. **Retest:** `trigger_dag_and_wait(dag_id)`
+2. **Retest:** `af runs trigger-wait <dag_id>`
 
 **Repeat the test → debug → fix loop until the DAG succeeds.**
 
 ---
 
-## MCP Tools Quick Reference
-
-| Phase | Tool | Purpose |
-|-------|------|---------|
-| Test | `trigger_dag_and_wait` | **Primary test method — start here** |
-| Test | `trigger_dag` | Start run (alternative) |
-| Test | `get_dag_run` | Check run status |
-| Debug | `diagnose_dag_run` | Comprehensive failure diagnosis |
-| Debug | `get_task_logs` | Get task output/errors |
-| Debug | `list_import_errors` | Check for parse errors (if DAG won't load) |
-| Debug | `get_dag_details` | Verify DAG config |
-| Debug | `explore_dag` | Full DAG inspection |
+## CLI Quick Reference
+
+| Phase | Command | Purpose |
+|-------|---------|---------|
+| Test | `af runs trigger-wait <dag_id>` | **Primary test method — start here** |
+| Test | `af runs trigger <dag_id>` | Start run (alternative) |
+| Test | `af runs get <dag_id> <run_id>` | Check run status |
+| Debug | `af runs diagnose <dag_id> <run_id>` | Comprehensive failure diagnosis |
+| Debug | `af tasks logs <dag_id> <run_id> <task_id>` | Get task output/errors |
+| Debug | `af dags errors` | Check for parse errors (if DAG won't load) |
+| Debug | `af dags get <dag_id>` | Verify DAG config |
+| Debug | `af dags explore <dag_id>` | Full DAG inspection |
+| Config | `af config connections` | List connections |
+| Config | `af config variables` | List variables |
 
 ---
 
 ## Testing Scenarios
 
 ### Scenario 1: Test a DAG (Happy Path)
 
-```
-1. trigger_dag_and_wait(dag_id) → Run and wait
-2. Success! Done.
+```bash
+af runs trigger-wait my_dag
+# Success! Done.
 ```
 
 ### Scenario 2: Test a DAG (With Failure)
 
-```
-1. trigger_dag_and_wait(dag_id) → Run and wait
-2. Failed → diagnose_dag_run    → Find failed tasks
-3. get_task_logs                → Get error details
-4. [Fix the issue]
-5. trigger_dag_and_wait(dag_id) → Retest
+```bash
+# 1. Run and wait
+af runs trigger-wait my_dag
+# Failed...
+
+# 2. Find failed tasks
+af runs diagnose my_dag manual__2025-01-14T...
+
+# 3. Get error details
+af tasks logs my_dag manual__2025-01-14T... extract_data
+
+# 4. [Fix the issue in DAG code]
+
+# 5. Retest
+af runs trigger-wait my_dag
 ```
 
 ### Scenario 3: DAG Doesn't Exist / Won't Load
 
-```
-1. trigger_dag_and_wait(dag_id) → Error: DAG not found
-2. list_import_errors           → Find parse error
-3. [Fix the issue]
-4. trigger_dag_and_wait(dag_id) → Retest
+```bash
+# 1. Trigger fails - DAG not found
+af runs trigger-wait my_dag
+# Error: DAG not found
+
+# 2. Find parse error
+af dags errors
+
+# 3. [Fix the issue in DAG code]
+
+# 4. Retest
+af runs trigger-wait my_dag
 ```
 
 ### Scenario 4: Debug a Failed Scheduled Run
 
-```
-1. diagnose_dag_run(dag_id, dag_run_id)  → Get failure summary
-2. get_task_logs(dag_id, dag_run_id, failed_task_id) → Get error
-3. [Fix the issue]
-4. trigger_dag_and_wait(dag_id)          → Retest
+```bash
+# 1. Get failure summary
+af runs diagnose my_dag scheduled__2025-01-14T...
+
+# 2. Get error from failed task
+af tasks logs my_dag scheduled__2025-01-14T... failed_task_id
+
+# 3. [Fix the issue]
+
+# 4. Retest
+af runs trigger-wait my_dag
 ```
 
 ### Scenario 5: Test with Custom Configuration
 
-```
-1. trigger_dag_and_wait(
-       dag_id="my_dag",
-       conf={"env": "staging", "batch_size": 100},
-       timeout=600
-   )
-2. [Analyze results]
+```bash
+af runs trigger-wait my_dag --conf '{"env": "staging", "batch_size": 100}' --timeout 600
 ```
 
 ### Scenario 6: Long-Running DAG
 
-```
-1. trigger_dag_and_wait(dag_id, timeout=3600)  → Wait up to 1 hour
-2. [If timed out] get_dag_run(dag_id, dag_run_id) → Check current state
+```bash
+# Wait up to 1 hour
+af runs trigger-wait my_dag --timeout 3600
+
+# If timed out, check current state
+af runs get my_dag manual__2025-01-14T...
 ```
 
 ---
@@ -351,7 +357,7 @@ Once you identify the issue:
 ### Common Error Patterns
 
 **Connection Refused / Timeout:**
-- Check `list_connections` for correct host/port
+- Check `af config connections` for correct host/port
 - Verify network connectivity to external system
 - Check if connection credentials are correct
 
PATCH

echo "Gold patch applied."
