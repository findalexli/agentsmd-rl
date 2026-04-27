#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "Write and run `scripts/create_solution.py` to create the publisher and solution " ".github/plugins/dataverse/skills/dv-init/SKILL.md" && grep -qF "If the file or the variable doesn't exist, the user has not initialized the Data" ".github/plugins/dataverse/skills/dv-mcp-configure/SKILL.md" && grep -qF "DO NOT USE WHEN: reading/writing data records (use dv-python-sdk)," ".github/plugins/dataverse/skills/dv-metadata/SKILL.md" && grep -qF "**Tool priority (always follow this order):** MCP (if available) for simple read" ".github/plugins/dataverse/skills/dv-overview/SKILL.md" && grep -qF "DO NOT USE WHEN: creating forms/views (use dv-metadata with Web API)," ".github/plugins/dataverse/skills/dv-python-sdk/SKILL.md" && grep -qF "DO NOT USE WHEN: initializing a workspace/repo (use dv-init)." ".github/plugins/dataverse/skills/dv-setup/SKILL.md" && grep -qF "DO NOT USE WHEN: creating tables/columns/forms/views (use dv-metadata)." ".github/plugins/dataverse/skills/dv-solution/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/dv-init/SKILL.md b/.github/plugins/dataverse/skills/dv-init/SKILL.md
@@ -1,12 +1,12 @@
 ---
-name: dataverse-init
+name: dv-init
 description: >
   Initialize a Dataverse workspace on a new machine or new repo.
   USE WHEN: ".env is missing", "setting up on a new machine", "starting a new project",
   "initialize workspace", "new repo", "first time setup", "configure MCP server",
   "MCP not connected", "load demo data", "sample data",
   "create a new environment", "select environment", "which environment".
-  DO NOT USE WHEN: installing tools (use dataverse-setup).
+  DO NOT USE WHEN: installing tools (use dv-setup).
 ---
 
 # Skill: Init
@@ -268,7 +268,7 @@ Both should succeed without error. Confirm the environment URL in the output mat
 
 **Defer (but don't skip)** if the user's immediate task can proceed without MCP (e.g., schema creation via SDK, solution import via PAC CLI). Complete the task first, then offer to configure MCP — it makes future conversational queries (reads, simple CRUD) much faster.
 
-If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill. **This is always the last step** because `claude mcp add` requires a Claude Code restart, which ends the current session.
+If MCP is needed and not yet configured, use the `dv-mcp-configure` skill. **This is always the last step** because `claude mcp add` requires a Claude Code restart, which ends the current session.
 
 Before triggering the MCP install command, inform the user:
 
@@ -349,7 +349,7 @@ Continue to the next steps.
 
 **This is where changes go into Dynamics first — never into the repo directly.**
 
-Write and run `scripts/create_solution.py` to create the publisher and solution in the environment using the Python SDK. The script **must** follow the publisher discovery flow from the `dataverse-solution` skill:
+Write and run `scripts/create_solution.py` to create the publisher and solution in the environment using the Python SDK. The script **must** follow the publisher discovery flow from the `dv-solution` skill:
 
 1. **Query existing publishers** in the environment (excluding Microsoft system publishers)
 2. **If a custom publisher exists**, show it to the user and ask: "Should I reuse this publisher (prefix: `<prefix>_`)?"
@@ -437,7 +437,7 @@ git commit -m "chore: initialize Dataverse workspace"
 - `claude mcp list` shows a `dataverse-*` server already registered
 - The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP) **and** the user has not explicitly mentioned MCP or asked to connect via MCP
 
-If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill.
+If MCP is needed and not yet configured, use the `dv-mcp-configure` skill.
 
 Before triggering the MCP install command, inform the user:
 
@@ -464,9 +464,9 @@ If the agent calls `list_tables` directly, MCP is connected. If it falls back to
 | Create/read/update/delete data records | MCP server |
 | Create a new table | MCP server |
 | Explore what tables/columns exist | MCP server (`list_tables`, `describe_table`) |
-| Add a column to an existing table | Web API (see `dataverse-metadata`) |
-| Create a relationship / lookup | Web API (see `dataverse-metadata`) |
-| Create or modify a form | Web API (see `dataverse-metadata`) |
-| Create or modify a view | Web API (see `dataverse-metadata`) |
+| Add a column to an existing table | Web API (see `dv-metadata`) |
+| Create a relationship / lookup | Web API (see `dv-metadata`) |
+| Create or modify a form | Web API (see `dv-metadata`) |
+| Create or modify a view | Web API (see `dv-metadata`) |
 
 For anything beyond data CRUD and basic table operations, use the Web API directly.
diff --git a/.github/plugins/dataverse/skills/dv-mcp-configure/SKILL.md b/.github/plugins/dataverse/skills/dv-mcp-configure/SKILL.md
@@ -1,18 +1,18 @@
 ---
-name: dataverse-mcp-configure
+name: dv-mcp-configure
 description: >
   Configure an MCP server for GitHub Copilot or Claude with your Dataverse environment.
   USE WHEN: "configure MCP", "set up MCP server", "MCP not working", "connect MCP to Dataverse",
       "add Dataverse to Copilot", "add Dataverse to Claude",
       "connect via MCP", "use MCP", "MCP tools not available", "no MCP tools", "MCP not configured".
-  DO NOT USE WHEN: workspace not initialized (use dataverse-init first), installing tools (use dataverse-setup).
+  DO NOT USE WHEN: workspace not initialized (use dv-init first), installing tools (use dv-setup).
 ---
 
 # Configure Dataverse MCP for GitHub Copilot or Claude
 
 This skill configures the Dataverse MCP server for GitHub Copilot or Claude with your organization's environment URL. Each organization is registered with a unique server name based on the org identifier (e.g., `DataverseMcporgbc9a965c`). 
 
-If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, do that first using the `dataverse-init` skill (do this by default when the user does not express a preference and just wants the MCP configured), which will set up the necessary environment variables. If they refuse, remind them to do that later when then attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP.
+If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, do that first using the `dv-init` skill (do this by default when the user does not express a preference and just wants the MCP configured), which will set up the necessary environment variables. If they refuse, remind them to do that later when then attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP.
 
 The parameters for the MCP server should be determined from context or environment variables where possible, and interactive prompts should only be used when it cannot be done.
 
@@ -34,7 +34,7 @@ Based on the result, set the `TOOL_TYPE` variable to either `copilot` or `claude
 Set the `MCP_CLIENT_ID` variable in `.env` based on the tool choice:
 - If `copilot`: `MCP_CLIENT_ID` = `aebc6443-996d-45c2-90f0-388ff96faa56`
 - If `claude`: `MCP_CLIENT_ID` = `0c412cc3-0dd6-449b-987f-05b053db9457`
-- If `claude` and the VSCode extension is used: set it to the same value as `CLIENT_ID` if already set, otherwise offer to create a new app registration following Scenario A, step 7 in the `dataverse-init` skill.
+- If `claude` and the VSCode extension is used: set it to the same value as `CLIENT_ID` if already set, otherwise offer to create a new app registration following Scenario A, step 7 in the `dv-init` skill.
 
 ### 1. Determine the MCP scope
 
@@ -103,7 +103,7 @@ Skip this step - Claude uses CLI commands to manage MCP servers, so we don't nee
 
 If the user provided a URL via command parameters it is: '$ARGUMENTS'. If the user mentioned the URL in the prompt, use it. Otherwise, take the URL from the `DATAVERSE_URL` variable in `.env`. If you have the URL, skip to step 4.
 
-If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Do that first using the `dataverse-init` skill (do this by default when the user does not express a preference and just wants the MCP configured), which will set up the necessary environment variables. If the user refuses, remind them to do that later when they attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP, and proceed to auto-discover the environment URL.
+If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Do that first using the `dv-init` skill (do this by default when the user does not express a preference and just wants the MCP configured), which will set up the necessary environment variables. If the user refuses, remind them to do that later when they attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP, and proceed to auto-discover the environment URL.
 
 **Auto-discovery priority order** — try each method in order, stop at the first that succeeds:
 
@@ -136,7 +136,7 @@ If PAC CLI is authenticated and `pac env list` returns results, present the envi
 >
 > Or type a URL manually.
 
-If the user wants to create a new environment, they can do so via `pac admin create` (see the `dataverse-init` skill's Environment Discovery flow).
+If the user wants to create a new environment, they can do so via `pac admin create` (see the `dv-init` skill's Environment Discovery flow).
 
 If PAC CLI is not installed or not authenticated, fall back to step 3b.
 
diff --git a/.github/plugins/dataverse/skills/dv-metadata/SKILL.md b/.github/plugins/dataverse/skills/dv-metadata/SKILL.md
@@ -1,12 +1,12 @@
 ---
-name: dataverse-metadata
+name: dv-metadata
 description: >
   Create or modify Dataverse tables, columns, relationships, forms, and views.
   USE WHEN: "add column", "create table", "add relationship", "lookup column", "create form",
   "create view", "modify form", "FormXml", "SavedQuery", "option set", "picklist",
   "MetadataService", "EntityDefinitions".
-  DO NOT USE WHEN: reading/writing data records (use dataverse-python-sdk),
-  exporting solutions (use dataverse-solution).
+  DO NOT USE WHEN: reading/writing data records (use dv-python-sdk),
+  exporting solutions (use dv-solution).
 ---
 
 # Skill: Metadata — Making Changes
diff --git a/.github/plugins/dataverse/skills/dv-overview/SKILL.md b/.github/plugins/dataverse/skills/dv-overview/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: dataverse-overview
+name: dv-overview
 description: >
   ALWAYS LOAD THIS SKILL FIRST for any Dataverse task. Contains hard rules that override all other skills.
   USE WHEN: ANY request involving Dataverse, Dynamics 365, Power Platform, tables, columns, solutions,
@@ -154,7 +154,7 @@ Understanding the real limits of each tool prevents hallucinated paths. This is
 | **Azure CLI** | App registrations, service principals, credential management | Dataverse-specific operations |
 | **GitHub CLI** | Repo management, GitHub secrets, Actions workflow status | Dataverse-specific operations |
 
-**Tool priority (always follow this order):** MCP (if available) for simple reads, queries, and ≤10 record CRUD → Python SDK for scripted data, bulk operations, schema creation, and analysis → Web API for operations the SDK doesn't cover (forms, views, option sets) → PAC CLI for solution lifecycle. MCP tools not in your tool list? → Load `dataverse-mcp-configure` to set them up (see below).
+**Tool priority (always follow this order):** MCP (if available) for simple reads, queries, and ≤10 record CRUD → Python SDK for scripted data, bulk operations, schema creation, and analysis → Web API for operations the SDK doesn't cover (forms, views, option sets) → PAC CLI for solution lifecycle. MCP tools not in your tool list? → Load `dv-mcp-configure` to set them up (see below).
 
 **Volume guidance:** MCP `create_record` is fine for 1–10 records. For 10+ records, use Python SDK `client.records.create(table, list_of_dicts)` — it uses `CreateMultiple` internally and handles batching. For data profiling and analytics beyond simple GROUP BY, use Python with pandas (see python-sdk skill). For aggregation queries (`$apply`), use the Web API directly.
 
@@ -167,7 +167,7 @@ If the user's request involves MCP — either explicitly ("connect via MCP", "us
 **If MCP tools are NOT available and the user explicitly asked for MCP:**
 1. **Do NOT silently fall back** to the Python SDK or Web API
 2. Tell the user: "Dataverse MCP tools aren't configured in this session yet."
-3. Load the `dataverse-mcp-configure` skill to set up the MCP server
+3. Load the `dv-mcp-configure` skill to set up the MCP server
 4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear (if running in Claude Code, remind them to resume the session correctly: "Remember to **use `claude --continue` to resume the session** without losing context"). Do not fall back to the SDK or proceed with other tools. Wait for the user to restart and come back.
 
 **If MCP tools are NOT available and the user asked a simple data question** (e.g., "how many accounts with 'jeff'?"):
diff --git a/.github/plugins/dataverse/skills/dv-python-sdk/SKILL.md b/.github/plugins/dataverse/skills/dv-python-sdk/SKILL.md
@@ -1,13 +1,13 @@
 ---
-name: dataverse-python-sdk
+name: dv-python-sdk
 description: >
   Use the official Microsoft Dataverse Python SDK for data operations.
   USE WHEN: "use the SDK", "query records", "create records", "bulk operations", "upsert",
   "Python script for Dataverse", "read data", "write data", "upload file",
   "bulk import", "CSV import", "load data", "data profiling", "data quality",
   "analyze data", "Jupyter notebook", "pandas", "notebook".
-  DO NOT USE WHEN: creating forms/views (use dataverse-metadata with Web API),
-  exporting solutions (use dataverse-solution with PAC CLI).
+  DO NOT USE WHEN: creating forms/views (use dv-metadata with Web API),
+  exporting solutions (use dv-solution with PAC CLI).
 ---
 
 # Skill: Python SDK
@@ -75,7 +75,7 @@ import requests  # WRONG for SDK-supported ops
 
 These are the ONLY operations where raw Web API (`get_token()` + `urllib`/`requests`) is acceptable:
 
-- **Forms** (FormXml) — use the Web API directly (see `dataverse-metadata`)
+- **Forms** (FormXml) — use the Web API directly (see `dv-metadata`)
 - **Views** (SavedQueries) — use the Web API directly
 - **Global option sets** — use the Web API directly
 - **N:N record association** (linking two records at runtime via `$ref` POST — distinct from N:N relationship *creation*, which the SDK handles)
diff --git a/.github/plugins/dataverse/skills/dv-setup/SKILL.md b/.github/plugins/dataverse/skills/dv-setup/SKILL.md
@@ -1,11 +1,11 @@
 ---
-name: dataverse-setup
+name: dv-setup
 description: >
   Set up a machine for Dataverse development — install tools and authenticate.
   USE WHEN: "install PAC CLI", "install tools", "command not found", "authenticate",
   "pac auth", "az login", "gh auth", "winget install", "setup machine",
   "missing tools", "new machine setup".
-  DO NOT USE WHEN: initializing a workspace/repo (use dataverse-init).
+  DO NOT USE WHEN: initializing a workspace/repo (use dv-init).
 ---
 
 # Skill: Setup
diff --git a/.github/plugins/dataverse/skills/dv-solution/SKILL.md b/.github/plugins/dataverse/skills/dv-solution/SKILL.md
@@ -1,11 +1,11 @@
 ---
-name: dataverse-solution
+name: dv-solution
 description: >
   Create, export, unpack, pack, import, and validate Dataverse solutions.
   USE WHEN: "export solution", "import solution", "pack solution", "unpack solution", "create solution",
   "pull from environment", "push to environment", "validate import", "check import errors",
   "check if table exists", "check if form is published", "verify deployment".
-  DO NOT USE WHEN: creating tables/columns/forms/views (use dataverse-metadata).
+  DO NOT USE WHEN: creating tables/columns/forms/views (use dv-metadata).
 ---
 
 # Skill: Solution
PATCH

echo "Gold patch applied."
