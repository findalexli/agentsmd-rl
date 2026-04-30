#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "Do not skip MCP configuration (step 8 in Scenario A, step 11 in Scenario B) unle" ".github/plugins/dataverse/skills/init/SKILL.md" && grep -qF "If the file or the variable doesn't exist, the user has not initialized the Data" ".github/plugins/dataverse/skills/mcp-configure/SKILL.md" && grep -qF "4. After MCP is configured, **stop here** \u2014 the session must be restarted for MC" ".github/plugins/dataverse/skills/overview/SKILL.md" && grep -qF "After any `winget` install, the new tool may not be in PATH until the shell is r" ".github/plugins/dataverse/skills/setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/init/SKILL.md b/.github/plugins/dataverse/skills/init/SKILL.md
@@ -15,10 +15,7 @@ description: >
 
 **Execute every numbered step in order.** Do not skip ahead to a later step, even if it appears more relevant to the user's immediate goal.
 
-**MCP setup exception:** MCP configuration (step 8 in Scenario A, step 11 in Scenario B) requires a Claude Code restart, which loses all session context. Therefore:
-- **Skip MCP setup entirely** if an MCP server is already configured (`.mcp.json` exists with a Dataverse server entry, or `claude mcp list` shows one).
-- **Defer MCP setup to the very last step** — after all scripts have been created and run, all metadata is live, and commits are done. This way the restart only loses the "done" state, not in-progress work.
-- Before triggering the restart, **write a brief status summary to `CLAUDE.md`** (or append to existing) so the next session knows what was completed.
+Do not skip MCP configuration (step 8 in Scenario A, step 11 in Scenario B) unless an MCP server is already configured (`.mcp.json` exists with a Dataverse server entry, or `claude mcp list` shows one).
 
 Two scenarios — handle both. But first, both scenarios share an environment discovery flow.
 
@@ -269,6 +266,7 @@ If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill
 Before triggering the MCP install command, inform the user:
 
 > MCP setup requires restarting Claude Code. All other setup steps are complete.
+> Remember to **use `claude --continue` to resume the session** without losing context.
 > After restart, you can verify MCP works by asking: "List the tables in my Dataverse environment."
 
 New machine setup is complete.
@@ -424,11 +422,12 @@ git commit -m "chore: initialize Dataverse workspace"
 - `claude mcp list` shows a `dataverse-*` server already registered
 - The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP) **and** the user has not explicitly mentioned MCP or asked to connect via MCP
 
-If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill. **This is always the last step** because `claude mcp add` requires a Claude Code restart, which ends the current session.
+If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill.
 
 Before triggering the MCP install command, inform the user:
 
 > MCP setup requires restarting Claude Code. All other setup steps are complete — your solution, tables, and scripts are committed.
+> Remember to **use `claude --continue` to resume the session** without losing context.
 > After restart, you can verify MCP works by asking: "List the tables in my Dataverse environment."
 
 ---
diff --git a/.github/plugins/dataverse/skills/mcp-configure/SKILL.md b/.github/plugins/dataverse/skills/mcp-configure/SKILL.md
@@ -12,7 +12,7 @@ description: >
 
 This skill configures the Dataverse MCP server for GitHub Copilot or Claude with your organization's environment URL. Each organization is registered with a unique server name based on the org identifier (e.g., `DataverseMcporgbc9a965c`). 
 
-If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, offer to do that first using the `dataverse-init` skill, which will set up the necessary environment variables. If they refuse, remind them to do that later when then attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP.
+If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, do that first using the `dataverse-init` skill (do this by default when the user does not express a preference and just wants the MCP configured), which will set up the necessary environment variables. If they refuse, remind them to do that later when then attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP.
 
 The parameters for the MCP server should be determined from context or environment variables where possible, and interactive prompts should only be used when it cannot be done.
 
@@ -103,7 +103,7 @@ Skip this step - Claude uses CLI commands to manage MCP servers, so we don't nee
 
 If the user provided a URL via command parameters it is: '$ARGUMENTS'. If the user mentioned the URL in the prompt, use it. Otherwise, take the URL from the `DATAVERSE_URL` variable in `.env`. If you have the URL, skip to step 4.
 
-If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Offer to do that first using the `dataverse-init` skill, which will set up the necessary environment variables. If they refuse, remind them to do that later when they attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP, and proceed to auto-discover the environment URL.
+If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Do that first using the `dataverse-init` skill (do this by default when the user does not express a preference and just wants the MCP configured), which will set up the necessary environment variables. If the user refuses, remind them to do that later when they attempt any operations that require PAC CLI, Python SDK or OData Web API instead of MCP, and proceed to auto-discover the environment URL.
 
 **Auto-discovery priority order** — try each method in order, stop at the first that succeeds:
 
@@ -382,41 +382,17 @@ Pause and give the user a chance to restart their editor before proceeding. Do n
 
 **If TOOL_TYPE is `claude`:**
 
-Offer to the user to install the Dataverse MCP server by running {CLAUDE_COMMAND} and, if they agree, run the command and provide the following instructions:
+Run {CLAUDE_COMMAND} to install the Dataverse MCP server, then tell the user:
 > To enable the MCP server, restart Claude Code.
+> Remember to **use `claude --continue` to resume the session** without losing context.
 >
 > After restarting, you will be able to:
 > - List all tables in your Dataverse environment
 > - Query records from any table
 > - Create, update, or delete records
 > - Explore your schema and relationships
 
-If you installed the MCP server, pause and give the user a chance to restart the session to enable it before proceeding. Do not perform any subsequent or parallel operations until the user responds.
-
-Otherwise provide the command with instructions:
-> To install the Dataverse MCP server, exit claude and run:
->
-> ```
-> {CLAUDE_COMMAND}
-> ```
->
-> **Optional: Validate your authentication setup first**
->
-> Before running the install command, you can optionally verify your Dataverse authentication is configured correctly by running:
->
-> ```
-> npx -y @microsoft/dataverse@latest mcp "{USER_URL}" --validate
-> ```
->
-> This command will check your authentication and print any error information if issues are found.
->
-> Then restart Claude Code.
->
-> After restarting, you will be able to:
-> - List all tables in your Dataverse environment
-> - Query records from any table
-> - Create, update, or delete records
-> - Explore your schema and relationships
+Pause and give the user a chance to restart the session to enable it before proceeding. Do not perform any subsequent or parallel operations until the user responds.
 
 ### 10. Troubleshooting
 
@@ -437,6 +413,11 @@ If something goes wrong, help the user check:
 - **If TOOL_TYPE is `claude`:**
   - Ensure the `claude` CLI is installed and available in their PATH
   - If the command fails, check that `npx` and `npm` are installed
-  - After running the command, they must restart Claude Code for the changes to take effect
+  - After running the command, they must restart Claude Code for the changes to take effect (remind them: "Remember to **use `claude --continue` to resume the session** without losing context")
   - They can verify the installation with `claude mcp list`
+  - To validate authentication independently, run:
+    ```
+    npx -y @microsoft/dataverse@latest mcp "{USER_URL}" --validate
+    ```
+    This checks credentials and prints error details if issues are found.
 
diff --git a/.github/plugins/dataverse/skills/overview/SKILL.md b/.github/plugins/dataverse/skills/overview/SKILL.md
@@ -158,7 +158,7 @@ If the user's request involves MCP — either explicitly ("connect via MCP", "us
 1. **Do NOT silently fall back** to the Python SDK or Web API
 2. Tell the user: "Dataverse MCP tools aren't configured in this session yet."
 3. Load the `dataverse-mcp-configure` skill to set up the MCP server
-4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear. Do not fall back to the SDK or proceed with other tools. Wait for the user to restart and come back.
+4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear (if running in Claude Code, remind them to resume the session correctly: "Remember to **use `claude --continue` to resume the session** without losing context"). Do not fall back to the SDK or proceed with other tools. Wait for the user to restart and come back.
 
 **If MCP tools ARE available**, proceed normally with the user's task.
 
diff --git a/.github/plugins/dataverse/skills/setup/SKILL.md b/.github/plugins/dataverse/skills/setup/SKILL.md
@@ -25,7 +25,7 @@ Check all in parallel. Install any that are missing.
 | Python 3 | `python --version` | `winget install Python.Python.3.12` |
 | Git | `git --version` | `winget install Git.Git` |
 
-After any `winget` install, the new tool may not be in PATH until the shell is restarted. If a tool is not found immediately after install, ask the user to close and reopen the terminal, then proceed.
+After any `winget` install, the new tool may not be in PATH until the shell is restarted. If a tool is not found immediately after install, ask the user to close and reopen the terminal (if running in Claude Code, remind them to resume the session correctly: "Remember to **use `claude --continue` to resume the session** without losing context"), then proceed.
 
 ### PAC CLI on Windows Git Bash
 
PATCH

echo "Gold patch applied."
