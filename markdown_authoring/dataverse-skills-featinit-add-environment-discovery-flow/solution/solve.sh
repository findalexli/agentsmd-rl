#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "> **Note:** `pac admin create` requires tenant admin or Power Platform admin per" ".github/plugins/dataverse/skills/init/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/init/SKILL.md b/.github/plugins/dataverse/skills/init/SKILL.md
@@ -4,7 +4,8 @@ description: >
   Initialize a Dataverse workspace on a new machine or new repo.
   USE WHEN: ".env is missing", "setting up on a new machine", "starting a new project",
   "initialize workspace", "new repo", "first time setup", "configure MCP server",
-  "MCP not connected", "load demo data", "sample data".
+  "MCP not connected", "load demo data", "sample data",
+  "create a new environment", "select environment", "which environment".
   DO NOT USE WHEN: installing tools (use dataverse-setup).
 ---
 
@@ -14,12 +15,108 @@ description: >
 
 **Execute every numbered step in order.** Do not skip ahead to a later step, even if it appears more relevant to the user's immediate goal.
 
-**MCP setup exception:** MCP configuration (step 5 in Scenario A, step 3's MCP part in Scenario B) requires a Claude Code restart, which loses all session context. Therefore:
+**MCP setup exception:** MCP configuration (step 8 in Scenario A, step 11 in Scenario B) requires a Claude Code restart, which loses all session context. Therefore:
 - **Skip MCP setup entirely** if an MCP server is already configured (`.mcp.json` exists with a Dataverse server entry, or `claude mcp list` shows one).
 - **Defer MCP setup to the very last step** — after all scripts have been created and run, all metadata is live, and commits are done. This way the restart only loses the "done" state, not in-progress work.
 - Before triggering the restart, **write a brief status summary to `CLAUDE.md`** (or append to existing) so the next session knows what was completed.
 
-Two scenarios — handle both.
+Two scenarios — handle both. But first, both scenarios share an environment discovery flow.
+
+---
+
+## Environment Discovery
+
+Before asking the user for a Dataverse environment URL, **check what is already available**. This avoids unnecessary questions and handles the common cases: the user is already connected, wants to pick from a list, or wants to create a new environment.
+
+### Step 1: Check existing auth
+
+```
+pac auth list
+pac org who
+```
+
+If PAC CLI is not authenticated at all (no profiles), ask the user:
+- "Do you want to connect to an existing environment or create a new one?"
+Then skip to Step 3 based on their answer.
+
+If PAC CLI has auth profiles, note the currently active environment and continue to Step 2.
+
+### Step 2: List available environments
+
+```
+pac env list
+```
+
+This shows all environments the user has access to (name, URL, type, state). Collect this list for the next step.
+
+### Step 3: Present options
+
+Show the user what you found and offer a choice:
+
+- **Use the currently active environment**: `<name>` (`<url>`) — if `pac org who` returned one
+- **Select a different existing environment** — show the list from `pac env list`
+- **Create a new environment**
+
+Wait for the user to choose. Do not assume.
+
+### Step 4a: If the user selects an existing environment
+
+If it is already the active auth profile, proceed — no connection changes needed.
+
+If it is a different environment, check whether an auth profile already exists for it (`pac auth list`). If so, select it:
+
+```
+pac auth select --name <profile-name>
+```
+
+If no profile exists, create one. **A browser window will open — sign in when prompted:**
+
+```
+pac auth create --name <profile-name> --environment <url>
+```
+
+Verify with `pac org who`.
+
+### Step 4b: If the user wants to create a new environment
+
+Ask for:
+- **Environment name** (required)
+- **Type**: `Developer` (default, free, single-user), `Sandbox`, or `Production`
+- **Region**: e.g., `unitedstates`, `europe`, `asia`, `australia`, `canada`, `japan`, `uk` (default: `unitedstates`)
+
+Run:
+
+```
+pac admin create --name "<name>" --type "<type>" --region "<region>"
+```
+
+Wait for completion (can take 1–3 minutes). The output contains the new environment URL. Connect to it:
+
+```
+pac auth create --name "<profile-name>" --environment "<new-url>"
+```
+
+Verify with `pac org who`.
+
+> **Note:** `pac admin create` requires tenant admin or Power Platform admin permissions. If it fails with a permissions error, guide the user to create the environment in the [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/) instead, then return to Step 4a to connect to it.
+
+### Step 5: Confirm and capture details
+
+Run `pac org who` one final time and **parse the output** to extract:
+- **Environment URL** → used as `DATAVERSE_URL` in `.env`
+- **Tenant ID** → used as `TENANT_ID` in `.env` (no separate HTTP call needed)
+
+Show the user the confirmed environment:
+
+> "Connected to `<name>` at `<url>`. I'll use this for all subsequent operations."
+
+If `pac org who` does not show a tenant ID (rare), fall back to the HTTP discovery method:
+
+```bash
+curl -sI https://<org>.crm.dynamics.com/api/data/v9.2/ \
+  | grep -i "WWW-Authenticate" \
+  | sed -n 's|.*login\.microsoftonline\.com/\([^/]*\).*|\1|p'
+```
 
 ---
 
@@ -37,7 +134,9 @@ ls .mcp.json 2>/dev/null && echo "found" || echo "missing"
 
 ### 2. Discover TENANT_ID automatically
 
-If the user does not know their TENANT_ID, derive it from the Dataverse environment URL — no portal login required:
+The `pac org who` output (from step 6's Environment Discovery) includes the tenant ID. Parse it directly — no separate HTTP call needed.
+
+If `pac org who` has not been run yet or does not contain a tenant ID, fall back to the HTTP method:
 
 ```bash
 curl -sI https://<org>.crm.dynamics.com/api/data/v9.2/ \
@@ -127,28 +226,9 @@ source ~/.bashrc
 
 ### 6. Connect to the environment
 
-Ask the user which environment they are setting up for. Do not assume.
-
-Check whether a connection already exists for that environment:
-
-```
-pac auth list
-pac org who
-```
-
-If a matching profile already exists, select it:
-
-```
-pac auth select --name <profile-name>
-```
+Run the **Environment Discovery** flow (see section above) to determine the target environment. The user may want to use the currently active environment, pick a different one, or create a new one — the discovery flow handles all three cases.
 
-If no connection exists yet, create one. Name the profile after the environment it targets (e.g., `dev`, `staging`, `prod`) — not a generic name. **A browser window will open — sign in with your Microsoft account when prompted:**
-
-```
-pac auth create --name <profile-name>
-```
-
-For service principal auth (non-interactive, used in CI):
+For service principal auth (non-interactive, used in CI), use this variant instead:
 
 ```
 pac auth create --name <profile-name> \
@@ -194,21 +274,19 @@ All commands below can be run directly by Claude — the user does not need to c
 
 Verify you are at the repo root.
 
-### 2. Discover TENANT_ID
+### 2. Select or create the target environment
 
-Always ask the user to confirm the Dataverse environment URL and pause to let the user respond even if you can derive it from `pac auth list` or other sources.
+Run the **Environment Discovery** flow (see section above) to determine which environment this project targets. The user may want to use an existing environment or create a new one — the discovery flow handles both.
 
-Do not perform any subsequent or parallel operations until the user answers. Do not assume.
-
-Before writing `.env`, auto-discover `TENANT_ID` from the Dataverse URL confirmed by the user:
+The discovery flow's final `pac org who` output includes the **tenant ID**. Parse it directly — no separate HTTP call needed. If the tenant ID is not in the output, fall back to:
 
 ```bash
 curl -sI https://<org>.crm.dynamics.com/api/data/v9.2/ \
   | grep -i "WWW-Authenticate" \
   | sed -n 's|.*login\.microsoftonline\.com/\([^/]*\).*|\1|p'
 ```
 
-Use the resulting GUID as `TENANT_ID` in `.env`. Only ask the user if this command fails.
+Use the resulting GUID as `TENANT_ID` in `.env`. Only ask the user if both methods fail.
 
 ### 3. Create .env and .gitignore
 
@@ -235,28 +313,15 @@ Copy `templates/CLAUDE.md` from the plugin to the repo root. Replace placeholder
 - `{{PUBLISHER_PREFIX}}` → leave as `TBD` for now (filled in after step 7 when the publisher is confirmed)
 - `{{PAC_AUTH_PROFILE}}` → `nonprod`
 
-### 6. Connect to the environment
+### 6. Verify the environment connection
 
-Ask the user which environment this new project targets. Do not assume.
-
-Check whether a connection already exists:
+The environment connection was established during step 2 (Environment Discovery). Verify it is still active:
 
 ```
-pac auth list
 pac org who
 ```
 
-If a matching profile appears, select it:
-
-```
-pac auth select --name <profile-name>
-```
-
-If not, connect now. Name the profile after the environment (e.g., `dev`, `staging`, `prod`). **A browser window will open — sign in with your Microsoft account when prompted:**
-
-```
-pac auth create --name <profile-name>
-```
+If the output does not match the target environment from step 2, re-run `pac auth select` or `pac auth create` to reconnect.
 
 Continue to the next steps.
 
PATCH

echo "Gold patch applied."
