#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "- \"What depends on this table?\" / \"What breaks if I change this?\" -> use the **t" "skills/airflow/SKILL.md" && grep -qF "> **For testing and debugging DAGs**, see the **testing-dags** skill which cover" "skills/authoring-dags/SKILL.md" && grep -qF "1. **Find the DAG**: Which DAG populates this table? Use `af dags list` and look" "skills/checking-freshness/SKILL.md" && grep -qF "Use `af runs get <dag_id> <dag_run_id>` to compare the failed run against recent" "skills/debugging-dags/SKILL.md" && grep -qF "Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af" "skills/testing-dags/SKILL.md" && grep -qF "1. **Check what the DAG produces**: Use `af dags source <dag_id>` to find output" "skills/tracing-downstream-lineage/SKILL.md" && grep -qF "1. **Search DAGs by name**: Use `af dags list` and look for DAG names matching t" "skills/tracing-upstream-lineage/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/airflow/SKILL.md b/skills/airflow/SKILL.md
@@ -118,16 +118,24 @@ Or CLI flags: `af --airflow-url http://localhost:8080 --token "$TOKEN" <command>
 - "Stop DAG X" / "Pause this workflow" -> `af dags pause <dag_id>`
 - "Resume DAG X" -> `af dags unpause <dag_id>`
 - "Are there any DAG errors?" -> `af dags errors`
+- "Create a new DAG" / "Write a pipeline" -> use the **authoring-dags** skill
 
 ### Run Operations
 - "What runs have executed?" -> `af runs list`
 - "Run DAG X" / "Trigger the pipeline" -> `af runs trigger <dag_id>`
 - "Run DAG X and wait" -> `af runs trigger-wait <dag_id>`
 - "Why did this run fail?" -> `af runs diagnose <dag_id> <run_id>`
+- "Test this DAG and fix if it fails" -> use the **testing-dags** skill
 
 ### Task Operations
 - "What tasks are in DAG X?" -> `af tasks list <dag_id>`
 - "Get task logs" / "Why did task fail?" -> `af tasks logs <dag_id> <run_id> <task_id>`
+- "Full root cause analysis" / "Diagnose and fix" -> use the **debugging-dags** skill
+
+### Data Operations
+- "Is the data fresh?" / "When was this table last updated?" -> use the **checking-freshness** skill
+- "Where does this data come from?" -> use the **tracing-upstream-lineage** skill
+- "What depends on this table?" / "What breaks if I change this?" -> use the **tracing-downstream-lineage** skill
 
 ### System Operations
 - "What version of Airflow?" -> `af config version`
@@ -260,7 +268,14 @@ af api variables/old_var -X DELETE
 
 ## Related Skills
 
-- `testing-dags` - Test DAGs with debugging and fixing cycles
-- `debugging-dags` - Comprehensive DAG failure diagnosis and root cause analysis
-- `authoring-dags` - Creating and editing DAG files with best practices
-- `managing-astro-local-env` - Starting/stopping local Airflow environment
+| Skill | Use when... |
+|-------|-------------|
+| **authoring-dags** | Creating or editing DAG files with best practices |
+| **testing-dags** | Iterative test -> debug -> fix -> retest cycles |
+| **debugging-dags** | Deep root cause analysis and failure diagnosis |
+| **checking-freshness** | Checking if data is up to date or stale |
+| **tracing-upstream-lineage** | Finding where data comes from |
+| **tracing-downstream-lineage** | Impact analysis -- what breaks if something changes |
+| **migrating-airflow-2-to-3** | Upgrading DAGs from Airflow 2.x to 3.x |
+| **managing-astro-local-env** | Starting, stopping, or troubleshooting local Airflow |
+| **setting-up-astro-project** | Initializing a new Astro/Airflow project |
diff --git a/skills/authoring-dags/SKILL.md b/skills/authoring-dags/SKILL.md
@@ -10,79 +10,56 @@ hooks:
 
 # DAG Authoring Skill
 
-This skill guides you through creating and validating Airflow DAGs using best practices and MCP tools.
+This skill guides you through creating and validating Airflow DAGs using best practices and `af` CLI commands.
 
-> **For testing and debugging DAGs**, see the **testing-dags** skill which covers the full test → debug → fix → retest workflow.
+> **For testing and debugging DAGs**, see the **testing-dags** skill which covers the full test -> debug -> fix -> retest workflow.
 
 ---
 
-## ⚠️ CRITICAL WARNING: Use MCP Tools, NOT CLI Commands ⚠️
+## Running the CLI
 
-> **STOP! Before running ANY Airflow-related command, read this.**
->
-> You MUST use MCP tools for ALL Airflow interactions. CLI commands like `astro dev run`, `airflow dags`, or shell commands to read logs are **FORBIDDEN**.
->
-> **Why?** MCP tools provide structured, reliable output. CLI commands are fragile, produce unstructured text, and often fail silently.
+Run all `af` commands using uvx (no installation required):
 
----
+```bash
+uvx --from astro-airflow-mcp af <command>
+```
 
-## CLI vs MCP Quick Reference
-
-**ALWAYS use Airflow MCP tools. NEVER use CLI commands.**
-
-| ❌ DO NOT USE | ✅ USE INSTEAD |
-|---------------|----------------|
-| `astro dev run dags list` | `list_dags` MCP tool |
-| `airflow dags list` | `list_dags` MCP tool |
-| `astro dev run dags test` | `trigger_dag_and_wait` MCP tool |
-| `airflow tasks test` | `trigger_dag_and_wait` MCP tool |
-| `cat` / `grep` on Airflow logs | `get_task_logs` MCP tool |
-| `find` in dags folder | `list_dags` or `explore_dag` MCP tool |
-| Any `astro dev run ...` | Equivalent MCP tool |
-| Any `airflow ...` CLI | Equivalent MCP tool |
-| `ls` on `/usr/local/airflow/dags/` | `list_dags` or `explore_dag` MCP tool |
-| `cat ... \| jq` to filter MCP results | Read the JSON directly from MCP response |
-
-**Remember:**
-- ✅ Airflow is ALREADY running — the MCP server handles the connection
-- ❌ Do NOT attempt to start, stop, or manage the Airflow environment
-- ❌ Do NOT use shell commands to check DAG status, logs, or errors
-- ❌ Do NOT use bash to parse or filter MCP tool results — read the JSON directly
-- ❌ Do NOT use `ls`, `find`, or `cat` on Airflow container paths (`/usr/local/airflow/...`)
-- ✅ ALWAYS use MCP tools — they return structured JSON you can read directly
+Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af`.
+
+---
 
 ## Workflow Overview
 
 ```
-┌─────────────────────────────────────┐
-│ 1. DISCOVER                         │
-│    Understand codebase & environment│
-└─────────────────────────────────────┘
-                 ↓
-┌─────────────────────────────────────┐
-│ 2. PLAN                             │
-│    Propose structure, get approval  │
-└─────────────────────────────────────┘
-                 ↓
-┌─────────────────────────────────────┐
-│ 3. IMPLEMENT                        │
-│    Write DAG following patterns     │
-└─────────────────────────────────────┘
-                 ↓
-┌─────────────────────────────────────┐
-│ 4. VALIDATE                         │
-│    Check import errors, warnings    │
-└─────────────────────────────────────┘
-                 ↓
-┌─────────────────────────────────────┐
-│ 5. TEST (with user consent)         │
-│    Trigger, monitor, check logs     │
-└─────────────────────────────────────┘
-                 ↓
-┌─────────────────────────────────────┐
-│ 6. ITERATE                          │
-│    Fix issues, re-validate          │
-└─────────────────────────────────────┘
++-----------------------------------------+
+| 1. DISCOVER                             |
+|    Understand codebase & environment    |
++-----------------------------------------+
+                 |
++-----------------------------------------+
+| 2. PLAN                                 |
+|    Propose structure, get approval      |
++-----------------------------------------+
+                 |
++-----------------------------------------+
+| 3. IMPLEMENT                            |
+|    Write DAG following patterns         |
++-----------------------------------------+
+                 |
++-----------------------------------------+
+| 4. VALIDATE                             |
+|    Check import errors, warnings        |
++-----------------------------------------+
+                 |
++-----------------------------------------+
+| 5. TEST (with user consent)             |
+|    Trigger, monitor, check logs         |
++-----------------------------------------+
+                 |
++-----------------------------------------+
+| 6. ITERATE                              |
+|    Fix issues, re-validate              |
++-----------------------------------------+
 ```
 
 ---
@@ -100,21 +77,21 @@ Use file tools to find existing patterns:
 
 ### Query the Airflow Environment
 
-Use MCP tools to understand what's available:
+Use `af` CLI commands to understand what's available:
 
-| Tool | Purpose |
-|------|---------|
-| `list_connections` | What external systems are configured |
-| `list_variables` | What configuration values exist |
-| `list_providers` | What operator packages are installed |
-| `get_airflow_version` | Version constraints and features |
-| `list_dags` | Existing DAGs and naming conventions |
-| `list_pools` | Resource pools for concurrency |
+| Command | Purpose |
+|---------|---------|
+| `af config connections` | What external systems are configured |
+| `af config variables` | What configuration values exist |
+| `af config providers` | What operator packages are installed |
+| `af config version` | Version constraints and features |
+| `af dags list` | Existing DAGs and naming conventions |
+| `af config pools` | Resource pools for concurrency |
 
 **Example discovery questions:**
-- "Is there a Snowflake connection?" → `list_connections`
-- "What Airflow version?" → `get_airflow_version`
-- "Are S3 operators available?" → `list_providers`
+- "Is there a Snowflake connection?" -> `af config connections`
+- "What Airflow version?" -> `af config version`
+- "Are S3 operators available?" -> `af config providers`
 
 ---
 
@@ -144,87 +121,93 @@ Write the DAG following best practices (see below). Key steps:
 
 ## Phase 4: Validate
 
-**Use the Airflow MCP as a feedback loop. Do NOT use CLI commands.**
+**Use `af` CLI as a feedback loop to validate your DAG.**
 
 ### Step 1: Check Import Errors
 
-After saving, call the MCP tool (Airflow will have already parsed the file):
+After saving, check for parse errors (Airflow will have already parsed the file):
 
-**MCP tool:** `list_import_errors`
+```bash
+af dags errors
+```
 
-- If your file appears → **fix and retry**
-- If no errors → **continue**
+- If your file appears -> **fix and retry**
+- If no errors -> **continue**
 
 Common causes: missing imports, syntax errors, missing packages.
 
 ### Step 2: Verify DAG Exists
 
-**MCP tool:** `get_dag_details(dag_id="your_dag_id")`
+```bash
+af dags get <dag_id>
+```
 
 Check: DAG exists, schedule correct, tags set, paused status.
 
 ### Step 3: Check Warnings
 
-**MCP tool:** `list_dag_warnings`
+```bash
+af dags warnings
+```
 
 Look for deprecation warnings or configuration issues.
 
 ### Step 4: Explore DAG Structure
 
-**MCP tool:** `explore_dag(dag_id="your_dag_id")`
+```bash
+af dags explore <dag_id>
+```
 
 Returns in one call: metadata, tasks, dependencies, source code.
 
 ---
 
 ## Phase 5: Test
 
-> **📘 See the testing-dags skill for comprehensive testing guidance.**
+> See the **testing-dags** skill for comprehensive testing guidance.
 
 Once validation passes, test the DAG using the workflow in the **testing-dags** skill:
 
-1. **Get user consent** — Always ask before triggering
-2. **Trigger and wait** — Use `trigger_dag_and_wait(dag_id, timeout=300)`
-3. **Analyze results** — Check success/failure status
-4. **Debug if needed** — Use `diagnose_dag_run` and `get_task_logs`
+1. **Get user consent** -- Always ask before triggering
+2. **Trigger and wait** -- `af runs trigger-wait <dag_id> --timeout 300`
+3. **Analyze results** -- Check success/failure status
+4. **Debug if needed** -- `af runs diagnose <dag_id> <run_id>` and `af tasks logs <dag_id> <run_id> <task_id>`
 
 ### Quick Test (Minimal)
 
-```
+```bash
 # Ask user first, then:
-trigger_dag_and_wait(dag_id="your_dag_id", timeout=300)
+af runs trigger-wait <dag_id> --timeout 300
 ```
 
-For the full test → debug → fix → retest loop, see **testing-dags**.
+For the full test -> debug -> fix -> retest loop, see **testing-dags**.
 
 ---
 
 ## Phase 6: Iterate
 
 If issues found:
 1. Fix the code
-2. Check for import errors with `list_import_errors` MCP tool
-3. Re-validate using MCP tools (Phase 4)
+2. Check for import errors: `af dags errors`
+3. Re-validate (Phase 4)
 4. Re-test using the **testing-dags** skill workflow (Phase 5)
 
-**Never use CLI commands to check status or logs. Always use MCP tools.**
-
 ---
 
-## MCP Tools Quick Reference
+## CLI Quick Reference
 
-| Phase | Tool | Purpose |
-|-------|------|---------|
-| Discover | `list_connections` | Available connections |
-| Discover | `list_variables` | Configuration values |
-| Discover | `list_providers` | Installed operators |
-| Discover | `get_airflow_version` | Version info |
-| Validate | `list_import_errors` | Parse errors (check first!) |
-| Validate | `get_dag_details` | Verify DAG config |
-| Validate | `list_dag_warnings` | Configuration warnings |
-| Validate | `explore_dag` | Full DAG inspection |
+| Phase | Command | Purpose |
+|-------|---------|---------|
+| Discover | `af config connections` | Available connections |
+| Discover | `af config variables` | Configuration values |
+| Discover | `af config providers` | Installed operators |
+| Discover | `af config version` | Version info |
+| Validate | `af dags errors` | Parse errors (check first!) |
+| Validate | `af dags get <dag_id>` | Verify DAG config |
+| Validate | `af dags warnings` | Configuration warnings |
+| Validate | `af dags explore <dag_id>` | Full DAG inspection |
 
-> **Testing tools** — See the **testing-dags** skill for `trigger_dag_and_wait`, `diagnose_dag_run`, `get_task_logs`, etc.
+> **Testing commands** -- See the **testing-dags** skill for `af runs trigger-wait`, `af runs diagnose`, `af tasks logs`, etc.
 
 ---
 
@@ -238,6 +221,6 @@ For code patterns and anti-patterns, see **[reference/best-practices.md](referen
 
 ## Related Skills
 
-- **testing-dags**: For testing DAGs, debugging failures, and the test → fix → retest loop
+- **testing-dags**: For testing DAGs, debugging failures, and the test -> fix -> retest loop
 - **debugging-dags**: For troubleshooting failed DAGs
 - **migrating-airflow-2-to-3**: For migrating DAGs to Airflow 3
diff --git a/skills/checking-freshness/SKILL.md b/skills/checking-freshness/SKILL.md
@@ -61,11 +61,11 @@ Report status using this scale:
 
 Check Airflow for the source pipeline:
 
-1. **Find the DAG**: Which DAG populates this table? Use `list_dags` and look for matching names.
+1. **Find the DAG**: Which DAG populates this table? Use `af dags list` and look for matching names.
 
 2. **Check DAG status**:
-   - Is the DAG paused? Use `get_dag_details`
-   - Did the last run fail? Use `get_dag_stats`
+   - Is the DAG paused? Use `af dags get <dag_id>`
+   - Did the last run fail? Use `af dags stats`
    - Is a run currently in progress?
 
 3. **Diagnose if needed**: If the DAG failed, use the **debugging-dags** skill to investigate.
diff --git a/skills/debugging-dags/SKILL.md b/skills/debugging-dags/SKILL.md
@@ -7,23 +7,35 @@ description: Comprehensive DAG failure diagnosis and root cause analysis. Use fo
 
 You are a data engineer debugging a failed Airflow DAG. Follow this systematic approach to identify the root cause and provide actionable remediation.
 
+## Running the CLI
+
+Run all `af` commands using uvx (no installation required):
+
+```bash
+uvx --from astro-airflow-mcp af <command>
+```
+
+Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af`.
+
+---
+
 ## Step 1: Identify the Failure
 
 If a specific DAG was mentioned:
-- Use `diagnose_dag_run` with the dag_id and dag_run_id (if provided)
-- If no run_id specified, use `get_dag_stats` to find recent failures
+- Run `af runs diagnose <dag_id> <dag_run_id>` (if run_id is provided)
+- If no run_id specified, run `af dags stats` to find recent failures
 
 If no DAG was specified:
-- Use `get_system_health` to find recent failures across all DAGs
-- List any import errors (broken DAG files)
+- Run `af health` to find recent failures across all DAGs
+- Check for import errors with `af dags errors`
 - Show DAGs with recent failures
 - Ask which DAG to investigate further
 
 ## Step 2: Get the Error Details
 
 Once you have identified a failed task:
 
-1. **Get task logs** using `get_task_logs` with the dag_id, dag_run_id, and task_id
+1. **Get task logs** using `af tasks logs <dag_id> <dag_run_id> <task_id>`
 2. **Look for the actual exception** - scroll past the Airflow boilerplate to find the real error
 3. **Categorize the failure type**:
    - **Data issue**: Missing data, schema change, null values, constraint violation
@@ -41,7 +53,7 @@ Gather additional context to understand WHY this happened:
 4. **Historical pattern**: Is this a recurring failure? Check if same task failed before
 5. **Timing**: Did this fail at an unusual time? (resource contention, maintenance windows)
 
-Use `get_dag_run` to compare the failed run against recent successful runs.
+Use `af runs get <dag_id> <dag_run_id>` to compare the failed run against recent successful runs.
 
 ## Step 4: Provide Actionable Output
 
@@ -70,5 +82,4 @@ How to prevent this from happening again:
 
 ### Quick Commands
 Provide ready-to-use commands:
-- To rerun the failed task: `airflow tasks run <dag_id> <task_id> <execution_date>`
-- To clear and retry: `airflow tasks clear <dag_id> -t <task_id> -s <start_date> -e <end_date>`
+- To clear and rerun failed tasks: `af tasks clear <dag_id> <run_id> <task_ids> -D`
diff --git a/skills/testing-dags/SKILL.md b/skills/testing-dags/SKILL.md
@@ -12,10 +12,10 @@ Use `af` commands to test, debug, and fix DAGs in iterative cycles.
 Run all `af` commands using uvx (no installation required):
 
 ```bash
-uvx --from astro-airflow-mcp@latest af <command>
+uvx --from astro-airflow-mcp af <command>
 ```
 
-Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp@latest af`.
+Throughout this document, `af` is shorthand for `uvx --from astro-airflow-mcp af`.
 
 ---
 
diff --git a/skills/tracing-downstream-lineage/SKILL.md b/skills/tracing-downstream-lineage/SKILL.md
@@ -18,8 +18,8 @@ Find everything that reads from this target:
 **For Tables:**
 
 1. **Search DAG source code**: Look for DAGs that SELECT from this table
-   - Use `list_dags` to get all DAGs
-   - Use `get_dag_source` to search for table references
+   - Use `af dags list` to get all DAGs
+   - Use `af dags source <dag_id>` to search for table references
    - Look for: `FROM target_table`, `JOIN target_table`
 
 2. **Check for dependent views**:
@@ -37,7 +37,7 @@ Find everything that reads from this target:
 
 **For DAGs:**
 
-1. **Check what the DAG produces**: Use `get_dag_source` to find output tables
+1. **Check what the DAG produces**: Use `af dags source <dag_id>` to find output tables
 2. **Then trace those tables' consumers** (recursive)
 
 ### Step 2: Build Dependency Tree
diff --git a/skills/tracing-upstream-lineage/SKILL.md b/skills/tracing-upstream-lineage/SKILL.md
@@ -20,15 +20,15 @@ Determine what we're tracing:
 
 Tables are typically populated by Airflow DAGs. Find the connection:
 
-1. **Search DAGs by name**: Use `list_dags` and look for DAG names matching the table name
+1. **Search DAGs by name**: Use `af dags list` and look for DAG names matching the table name
    - `load_customers` -> `customers` table
    - `etl_daily_orders` -> `orders` table
 
-2. **Explore DAG source code**: Use `get_dag_source` to read the DAG definition
+2. **Explore DAG source code**: Use `af dags source <dag_id>` to read the DAG definition
    - Look for INSERT, MERGE, CREATE TABLE statements
    - Find the target table in the code
 
-3. **Check DAG tasks**: Use `list_tasks` to see what operations the DAG performs
+3. **Check DAG tasks**: Use `af tasks list <dag_id>` to see what operations the DAG performs
 
 ### Step 3: Trace Data Sources
 
@@ -77,7 +77,7 @@ TARGET: analytics.orders_daily
 
 For each upstream source:
 - **Tables**: Check freshness with the **checking-freshness** skill
-- **DAGs**: Check recent run status with `get_dag_stats`
+- **DAGs**: Check recent run status with `af dags stats`
 - **External systems**: Note connection info from DAG code
 
 ## Lineage for Columns
PATCH

echo "Gold patch applied."
