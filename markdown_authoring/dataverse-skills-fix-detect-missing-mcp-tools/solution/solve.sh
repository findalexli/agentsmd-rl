#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "- The user's immediate task does not require MCP (e.g., they asked to create tab" ".github/plugins/dataverse/skills/init/SKILL.md" && grep -qF "If the file or the variable doesn't exist, the user has not initialized the Data" ".github/plugins/dataverse/skills/mcp-configure/SKILL.md" && grep -qF "**When in doubt:** MCP tools not in your tool list? \u2192 Load `dataverse-mcp-config" ".github/plugins/dataverse/skills/overview/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/init/SKILL.md b/.github/plugins/dataverse/skills/init/SKILL.md
@@ -173,7 +173,7 @@ Both should succeed without error. Confirm the environment URL in the output mat
 **Skip this step entirely** if any of the following are true:
 - `.mcp.json` already exists and contains a Dataverse server entry
 - `claude mcp list` shows a `dataverse-*` server already registered
-- The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP)
+- The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP) **and** the user has not explicitly mentioned MCP or asked to connect via MCP
 
 If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill. **This is always the last step** because `claude mcp add` requires a Claude Code restart, which ends the current session.
 
@@ -348,7 +348,7 @@ git commit -m "chore: initialize Dataverse workspace"
 
 - `.mcp.json` already exists and contains a Dataverse server entry
 - `claude mcp list` shows a `dataverse-*` server already registered
-- The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP)
+- The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP) **and** the user has not explicitly mentioned MCP or asked to connect via MCP
 
 If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill. **This is always the last step** because `claude mcp add` requires a Claude Code restart, which ends the current session.
 
diff --git a/.github/plugins/dataverse/skills/mcp-configure/SKILL.md b/.github/plugins/dataverse/skills/mcp-configure/SKILL.md
@@ -3,7 +3,8 @@ name: dataverse-mcp-configure
 description: >
   Configure an MCP server for GitHub Copilot or Claude with your Dataverse environment.
   USE WHEN: "configure MCP", "set up MCP server", "MCP not working", "connect MCP to Dataverse",
-      "add Dataverse to Copilot", "add Dataverse to Claude".
+      "add Dataverse to Copilot", "add Dataverse to Claude",
+      "connect via MCP", "use MCP", "MCP tools not available", "no MCP tools", "MCP not configured".
   DO NOT USE WHEN: workspace not initialized (use dataverse-init first), installing tools (use dataverse-setup).
 ---
 
@@ -102,21 +103,48 @@ Skip this step - Claude uses CLI commands to manage MCP servers, so we don't nee
 
 If the user provided a URL via command parameters it is: '$ARGUMENTS'. If the user mentioned the URL in the prompt, use it. Otherwise, take the URL from the `DATAVERSE_URL` variable in `.env`. If you have the URL, skip to step 4.
 
-If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Offer to do that first using the `dataverse-init` skill, which will set up the necessary environment variables. If they refuse, remind them to do that later when then attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP, and ask the user:
+If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Offer to do that first using the `dataverse-init` skill, which will set up the necessary environment variables. If they refuse, remind them to do that later when they attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP, and proceed to auto-discover the environment URL.
 
-> How would you like to provide your Dataverse environment URL?
-> 1. **Auto-discover** — List available environments from your Azure account (requires Azure CLI)
-> 2. **Manual entry** — Enter the URL directly
+**Auto-discovery priority order** — try each method in order, stop at the first that succeeds:
 
-Based on their choice:
-- If **Auto-discover**: Proceed to step 3a
-- If **Manual entry**: Skip to step 3b
+1. **PAC CLI** (preferred) → step 3a
+2. **Azure CLI** (fallback) → step 3b
+3. **Manual entry** (last resort) → step 3c
 
-### 3a. Auto-discover environments
+### 3a. Auto-discover via PAC CLI (preferred)
+
+Check if PAC CLI is available:
+
+```
+pac --version
+```
+
+If available, check auth and list environments:
+
+```
+pac auth list
+pac org who
+pac env list
+```
+
+If PAC CLI is authenticated and `pac env list` returns results, present the environments to the user:
+
+> I found the following Dataverse environments via PAC CLI. Which one would you like to configure MCP for?
+>
+> 1. My Dev Org — `https://orgfbb52bb7.crm.dynamics.com`
+> 2. Another Env — `https://orgabc123.crm.dynamics.com`
+>
+> Or type a URL manually.
+
+If the user wants to create a new environment, they can do so via `pac admin create` (see the `dataverse-init` skill's Environment Discovery flow).
+
+If PAC CLI is not installed or not authenticated, fall back to step 3b.
+
+### 3b. Auto-discover via Azure CLI (fallback)
 
 **Check prerequisites:**
 - Verify Azure CLI (`az`) is installed (check with `which az` or `where az` on Windows)
-- If not installed, inform the user and fall back to step 3b
+- If not installed, inform the user and fall back to step 3c
 
 **Make the API call:**
 
@@ -166,11 +194,11 @@ Based on their choice:
 
 If the user selects an already-configured environment, confirm that they want to re-register it (e.g. to change the endpoint type) before proceeding.
 
-If the user types "manual", fall back to step 3b.
+If the user types "manual", fall back to step 3c.
 
-**If the API call fails** (user not logged in, network error, no environments found, or any other error), tell the user what went wrong and fall back to step 3b.
+**If the API call fails** (user not logged in, network error, no environments found, or any other error), tell the user what went wrong and fall back to step 3c.
 
-### 3b. Manual entry — ask for the URL
+### 3c. Manual entry — ask for the URL
 
 Ask the user to provide their environment URL directly:
 
@@ -319,6 +347,8 @@ Tell the user:
 > - Create, update, or delete records
 > - Explore your schema and relationships
 
+Pause and give the user a chance to restart their editor before proceeding. Do not perform any subsequent or parallel operations until the user responds — they need MCP tools to be active first.
+
 **If TOOL_TYPE is `claude`:**
 
 Offer to the user to install the Dataverse MCP server by running {CLAUDE_COMMAND} and, if they agree, run the command and provide the following instructions:
diff --git a/.github/plugins/dataverse/skills/overview/SKILL.md b/.github/plugins/dataverse/skills/overview/SKILL.md
@@ -144,12 +144,24 @@ Understanding the real limits of each tool prevents hallucinated paths. This is
 | **Azure CLI** | App registrations, service principals, credential management | Dataverse-specific operations |
 | **GitHub CLI** | Repo management, GitHub secrets, Actions workflow status | Dataverse-specific operations |
 
-**When in doubt:** MCP for conversational data work (single records, simple queries) → Python SDK for scripted data, bulk operations, schema creation, and analysis → Web API for metadata the SDK doesn't cover (forms, views, option sets) → PAC CLI for solution lifecycle.
+**When in doubt:** MCP tools not in your tool list? → Load `dataverse-mcp-configure` to set them up (see below). MCP for conversational data work (single records, simple queries) → Python SDK for scripted data, bulk operations, schema creation, and analysis → Web API for metadata the SDK doesn't cover (forms, views, option sets) → PAC CLI for solution lifecycle.
 
 **Volume guidance:** MCP `create_record` is fine for 1–10 records. For 10+ records, use Python SDK `client.records.create(table, list_of_dicts)` — it uses `CreateMultiple` internally and handles batching. For data profiling and analytics beyond simple GROUP BY, use Python with pandas (see python-sdk skill). For aggregation queries (`$apply`), use the Web API directly.
 
 Note: The Python SDK is in **preview** — breaking changes possible.
 
+### MCP Availability Check
+
+If the user's request involves MCP — either explicitly ("connect via MCP", "use MCP", "query via MCP") or implicitly (conversational data queries where MCP would be the natural tool) — check whether Dataverse MCP tools are available in your current tool list (e.g., `list_tables`, `describe_table`, `read_query`, `create_record`).
+
+**If MCP tools are NOT available:**
+1. **Do NOT silently fall back** to the Python SDK or Web API
+2. Tell the user: "Dataverse MCP tools aren't configured in this session yet."
+3. Load the `dataverse-mcp-configure` skill to set up the MCP server
+4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear. Do not fall back to the SDK or proceed with other tools. Wait for the user to restart and come back.
+
+**If MCP tools ARE available**, proceed normally with the user's task.
+
 ---
 
 ## Available Skills
PATCH

echo "Gold patch applied."
