#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "Do not skip MCP configuration (step 9 in Scenario A, step 12 in Scenario B) unle" ".github/plugins/dataverse/skills/init/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/init/SKILL.md b/.github/plugins/dataverse/skills/init/SKILL.md
@@ -15,7 +15,7 @@ description: >
 
 **Execute every numbered step in order.** Do not skip ahead to a later step, even if it appears more relevant to the user's immediate goal.
 
-Do not skip MCP configuration (step 8 in Scenario A, step 11 in Scenario B) unless an MCP server is already configured (`.mcp.json` exists with a Dataverse server entry, or `claude mcp list` shows one).
+Do not skip MCP configuration (step 9 in Scenario A, step 12 in Scenario B) unless an MCP server is already configured (`.mcp.json` exists with a Dataverse server entry, or `claude mcp list` shows one).
 
 Two scenarios — handle both. But first, both scenarios share an environment discovery flow.
 
@@ -245,7 +245,13 @@ pac auth create --name <profile-name> \
 
 > **Multi-environment repos:** If the team deploys to multiple environments from the same repo, each developer's `.env` represents their current target. Consider `.env.dev`, `.env.staging`, etc., with a pattern like `cp .env.dev .env` to switch targets. Each developer manages their own local `.env`.
 
-### 7. Verify the connection
+### 7. Install / upgrade Python dependencies
+
+```
+pip install --upgrade azure-identity requests PowerPlatform-Dataverse-Client
+```
+
+### 8. Verify the connection
 
 ```
 pac org who
@@ -254,7 +260,7 @@ python scripts/auth.py
 
 Both should succeed without error. Confirm the environment URL in the output matches the intended target.
 
-### 8. Configure MCP server (if not already configured)
+### 9. Configure MCP server (if not already configured)
 
 **Skip this step entirely** if any of the following are true:
 - `.mcp.json` already exists and contains a Dataverse server entry
@@ -320,7 +326,13 @@ Copy `templates/CLAUDE.md` from the plugin to the repo root. Replace placeholder
 - `{{PUBLISHER_PREFIX}}` → leave as `TBD` for now (filled in after step 7 when the publisher is confirmed)
 - `{{PAC_AUTH_PROFILE}}` → `nonprod`
 
-### 6. Verify the environment connection
+### 6. Install / upgrade Python dependencies
+
+```
+pip install --upgrade azure-identity requests PowerPlatform-Dataverse-Client
+```
+
+### 7. Verify the environment connection
 
 The environment connection was established during step 2 (Environment Discovery). Verify it is still active:
 
@@ -332,7 +344,7 @@ If the output does not match the target environment from step 2, re-run `pac aut
 
 Continue to the next steps.
 
-### 7. Create the solution and metadata in the environment
+### 8. Create the solution and metadata in the environment
 
 **This is where changes go into Dynamics first — never into the repo directly.**
 
@@ -356,7 +368,7 @@ Then write and run any scripts needed to create tables, columns, or other metada
 python scripts/create_tables.py
 ```
 
-### 8. Pull the environment state to the repo
+### 9. Pull the environment state to the repo
 
 **After all changes are live in the environment, pull them into the repo:**
 
@@ -366,7 +378,7 @@ pac solution unpack --zipfile ./solutions/<SOLUTION_NAME>.zip --folder ./solutio
 rm ./solutions/<SOLUTION_NAME>.zip
 ```
 
-### 9. Load demo data (optional)
+### 10. Load demo data (optional)
 
 If the user wants sample data for testing (accounts, contacts, opportunities), use the built-in Dataverse sample data feature:
 
@@ -407,14 +419,14 @@ else:
 
 To remove demo data later, call `UninstallSampleData` the same way.
 
-### 10. Commit
+### 11. Commit
 
 ```
 git add .gitignore CLAUDE.md solutions/ plugins/ scripts/
 git commit -m "chore: initialize Dataverse workspace"
 ```
 
-### 11. Configure MCP server (if not already configured)
+### 12. Configure MCP server (if not already configured)
 
 **Skip this step entirely** if any of the following are true:
 
PATCH

echo "Gold patch applied."
