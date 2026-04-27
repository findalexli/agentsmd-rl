#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "**Execute every numbered step in order.** Do not skip ahead to a later step, eve" ".github/plugins/dataverse/skills/init/SKILL.md" && grep -qF "If you installed the MCP server, pause and give the user a chance to restart the" ".github/plugins/dataverse/skills/mcp-configure/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/init/SKILL.md b/.github/plugins/dataverse/skills/init/SKILL.md
@@ -12,6 +12,8 @@ description: >
 
 > **Environment-First Rule** — All metadata (solutions, columns, tables, forms, views) and plugin registrations are created **in the Dynamics environment** via API or scripts, then pulled into the repo. Never write or edit solution XML by hand to create new components. This rule applies to every step in both scenarios below.
 
+**Execute every numbered step in order.** Do not skip ahead to a later step, even if it appears more relevant to the user's immediate goal. Steps that seem unrelated to the current task (e.g., MCP setup when the user asked about tables) are still required — they enable the user's workflow in future sessions.
+
 Two scenarios — handle both.
 
 ---
@@ -174,7 +176,11 @@ Verify you are at the repo root.
 
 ### 2. Discover TENANT_ID
 
-Before writing `.env`, auto-discover `TENANT_ID` from the Dataverse URL (the user must provide the URL first):
+Always ask the user to confirm the Dataverse environment URL and pause to let the user respond even if you can derive it from `pac auth list` or other sources.
+
+Do not perform any subsequent or parallel operations until the user answers. Do not assume.
+
+Before writing `.env`, auto-discover `TENANT_ID` from the Dataverse URL confirmed by the user:
 
 ```bash
 curl -sI https://<org>.crm.dynamics.com/api/data/v9.2/ \
@@ -186,7 +192,9 @@ Use the resulting GUID as `TENANT_ID` in `.env`. Only ask the user if this comma
 
 ### 3. Create .env, MCP config, and .gitignore
 
-Follow steps 3–4 from Scenario A above. Ask the user for DATAVERSE_URL and SOLUTION_NAME if not already known. Set up MCP following step 5 from Scenario A. Skip CLIENT_ID/CLIENT_SECRET if the user authenticates interactively. Device code tokens are cached automatically via AuthenticationRecord persistence.
+Follow steps 3–4 from Scenario A above. Ask the user for SOLUTION_NAME if not already known (but use the DATAVERSE_URL you obtained and confirmed in step 2).
+
+Set up MCP following step 5 from Scenario A.
 
 ### 4. Create the directory structure
 
diff --git a/.github/plugins/dataverse/skills/mcp-configure/SKILL.md b/.github/plugins/dataverse/skills/mcp-configure/SKILL.md
@@ -330,6 +330,8 @@ Offer to the user to install the Dataverse MCP server by running {CLAUDE_COMMAND
 > - Create, update, or delete records
 > - Explore your schema and relationships
 
+If you installed the MCP server, pause and give the user a chance to restart the session to enable it before proceeding. Do not perform any subsequent or parallel operations until the user responds.
+
 Otherwise provide the command with instructions:
 > To install the Dataverse MCP server, exit claude and run:
 >
PATCH

echo "Gold patch applied."
