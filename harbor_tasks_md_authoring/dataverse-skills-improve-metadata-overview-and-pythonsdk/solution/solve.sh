#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "**Mitigation:** Add a 3-5 second delay after table creation before adding column" ".github/plugins/dataverse/skills/metadata/SKILL.md" && grep -qF "**Do not proceed until the user explicitly confirms.** This is the single most i" ".github/plugins/dataverse/skills/overview/SKILL.md" && grep -qF "- If a record insert fails with \"Invalid property\", verify the lookup column's l" ".github/plugins/dataverse/skills/python-sdk/SKILL.md" && grep -qF "If the header was misspelled or the solution doesn't exist, components will be c" ".github/plugins/dataverse/skills/solution/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/metadata/SKILL.md b/.github/plugins/dataverse/skills/metadata/SKILL.md
@@ -11,6 +11,10 @@ description: >
 
 # Skill: Metadata — Making Changes
 
+**Before the first metadata change in a session, confirm the target environment with the user.** See the Multi-Environment Rule in the overview skill for the full confirmation flow.
+
+---
+
 ## How Changes Are Made: Environment-First
 
 **Do not write solution XML by hand to create new tables, columns, forms, or views.**
@@ -109,11 +113,14 @@ attribute = {
                     "LocalizedLabels": [{"@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                                           "Label": "Description", "LanguageCode": 1033}]},
     "RequiredLevel": {"Value": "None"},
-    "MaxLength": 500
+    "MaxLength": 500,
+    "FormatName": {"Value": "Text"}   # Always use "Text" — see FormatName reference below
 }
 # POST to /api/data/v9.2/EntityDefinitions(LogicalName='new_projectbudget')/Attributes
 ```
 
+**Valid FormatName values for StringAttributeMetadata:** `Text`, `TextArea`, `Url`, `TickerSymbol`, `PhoneticGuide`, `VersionNumber`, `Phone`. Note: `Email` is **not** a valid FormatName despite being a common assumption — use `Text` for email columns.
+
 **Currency column:**
 ```python
 attribute = {
@@ -426,6 +433,65 @@ When creating forms via the Web API (`POST /api/data/v9.2/systemforms`), FormXml
 
 ---
 
+## After Creating Columns: Report Logical Names
+
+After creating columns (via Web API or MCP), **always report the actual logical names** to the user. Column names may be normalized or prefixed in ways the user doesn't expect. Summarize in a table:
+
+| Display Name | Logical Name | Type |
+|---|---|---|
+| Email | cr9ac_email | String |
+| Tier | cr9ac_tier | Picklist |
+| Customer | cr9ac_customerid | Lookup |
+
+This prevents downstream failures when the user tries to insert data using incorrect column names.
+
+---
+
+## Common Web API Error Codes
+
+| Error Code | Meaning | Recovery |
+|---|---|---|
+| `0x80040216` | Transient metadata cache error. Column or table metadata not yet propagated. | Wait 3-5 seconds and retry. Usually succeeds on second attempt. |
+| `0x80048d19` | Invalid property in payload. A field name doesn't match any column on the table. | Check logical column names — use `EntityDefinitions(LogicalName='...')/Attributes` to verify. |
+| `0x80040237` | Schema name already exists. | Verify the column/table exists before creating a new one — it may have been created by a previous timed-out call. |
+| `0x8004431a` | Publisher prefix mismatch. | Ensure all schema names use the solution's publisher prefix. |
+| `0x80060891` | Metadata cache not ready after table creation. | Call `GET EntityDefinitions(LogicalName='...')` first to force cache refresh, then retry. |
+
+Always translate error codes to plain English before presenting them to the user.
+
+---
+
+## Metadata Propagation Delays
+
+After creating tables or columns via the Web API, metadata propagation can take 3-10 seconds. Common symptoms:
+
+- Picklist columns fail with `0x80040216` immediately after table creation
+- Lookup `@odata.bind` operations fail with "Invalid property" shortly after column creation
+- `update_table` (MCP) fails with "EntityId not found in MetadataCache"
+
+**Mitigation:** Add a 3-5 second delay after table creation before adding columns. After creating lookup columns, wait 5-10 seconds before inserting records that use `@odata.bind` on those lookups. If a column creation fails, verify it doesn't already exist, then retry once.
+
+---
+
+## Session Closing: Pull to Repo
+
+**After every metadata session, perform the pull-to-repo sequence.** This is not optional — work that exists only in the environment is lost if the environment is reset.
+
+```bash
+pac solution export --name <SOLUTION_NAME> --path ./solutions/<SOLUTION_NAME>.zip --managed false
+pac solution unpack --zipfile ./solutions/<SOLUTION_NAME>.zip --folder ./solutions/<SOLUTION_NAME>
+rm ./solutions/<SOLUTION_NAME>.zip
+git add ./solutions/<SOLUTION_NAME>
+git commit -m "feat: <description of change>"
+```
+
+If you used the `MSCRM.SolutionName` header during creation, verify components are in the solution before exporting:
+```bash
+pac solution list-components --solutionUniqueName <SOLUTION_NAME> --environment <url>
+```
+
+---
+
 ## MCP Table Creation Notes
 
 When using MCP `create_table` or `update_table`:
diff --git a/.github/plugins/dataverse/skills/overview/SKILL.md b/.github/plugins/dataverse/skills/overview/SKILL.md
@@ -92,22 +92,21 @@ Skills exist as **Claude's knowledge**, not as user-facing commands. Each skill
 
 ---
 
-## Multi-Environment Rule
+## Multi-Environment Rule (MANDATORY)
 
 Pro-dev scenarios involve multiple environments (dev, test, staging, prod) and multiple sets of credentials. **Never assume** the active PAC auth profile, values in `.env`, or anything from memory or a previous session reflects the correct target for the current task.
 
-**Before any operation that touches a specific environment** — deploying a plugin, pushing a solution, registering a step, running a script against the Web API — ask the user:
+**Before the FIRST operation that touches a specific environment** — creating a table, deploying a plugin, pushing a solution, inserting data — you MUST:
 
-> "Which environment should I target for this? Please confirm the URL."
+1. Show the user the environment URL you intend to use
+2. Ask them to confirm it is correct
+3. Run `pac org who` to verify the active connection matches
 
-Then verify the active PAC profile matches:
+> "I'm about to make changes to `<URL>`. Is this the correct target environment?"
 
-```bash
-pac auth list
-pac org who
-```
+**Do not proceed until the user explicitly confirms.** This is the single most important safety check in the plugin. Skipping it risks making irreversible changes to the wrong environment.
 
-The more impactful the operation (plugin deploy, solution import, step registration), the more important this confirmation is. Do not proceed against an environment the user hasn't explicitly confirmed in the current session.
+Once confirmed for a session, you do not need to re-confirm for every subsequent operation in the same session against the same environment.
 
 ---
 
@@ -186,9 +185,22 @@ When running in Git Bash on Windows (the default for Claude Code on Windows):
 
 ---
 
-## After Any Change: Pull to Repo
+## Before Any Metadata Change: Confirm Solution
+
+Before creating tables, columns, or other metadata, ensure a solution exists to contain the work:
+
+1. Ask the user: "What solution should these components go into?"
+2. If a solution name is in `.env` (`SOLUTION_NAME`), confirm it with the user
+3. If no solution exists yet, create one (see the `solution` skill)
+4. Use the `MSCRM.SolutionName` header on all Web API metadata calls to auto-add components
+
+Creating metadata without a solution means it exists only in the default solution and cannot be cleanly exported or deployed. Always solution-first.
+
+---
+
+## After Any Change: Pull to Repo (MANDATORY)
 
-Any time you make a metadata change (via MCP, Web API, or the maker portal), end the session by pulling:
+Any time you make a metadata change (via MCP, Web API, or the maker portal), **you must** end the session by pulling:
 
 ```bash
 pac solution export --name <SOLUTION_NAME> --path ./solutions/<SOLUTION_NAME>.zip --managed false
diff --git a/.github/plugins/dataverse/skills/python-sdk/SKILL.md b/.github/plugins/dataverse/skills/python-sdk/SKILL.md
@@ -95,6 +95,11 @@ guid = client.records.create("new_projectbudget", {
 print(f"Created: {guid}")
 ```
 
+**Lookup binding (`@odata.bind`) notes:**
+- If you just created lookup columns, wait 5-10 seconds before inserting records that reference them. Metadata propagation delays can cause "Invalid property" errors.
+- Choice (picklist) columns use integer values, not strings: `"new_status": 100000000` (not `"Draft"`).
+- If a record insert fails with "Invalid property", verify the lookup column's logical name and navigation property name by querying `EntityDefinitions(LogicalName='...')/Attributes`.
+
 ### Query records (multi-record — returns page iterator)
 ```python
 for page in client.records.get(
diff --git a/.github/plugins/dataverse/skills/solution/SKILL.md b/.github/plugins/dataverse/skills/solution/SKILL.md
@@ -63,6 +63,24 @@ Common component type codes:
 
 Repeat the command for each component you need to add.
 
+### Alternative: Auto-add via MSCRM.SolutionName Header
+
+When creating metadata via the Web API, include the `MSCRM.SolutionName` header to auto-add components to the solution:
+```python
+headers = {
+    "Authorization": f"Bearer {token}",
+    "Content-Type": "application/json",
+    "MSCRM.SolutionName": "<UniqueName>"
+}
+```
+
+**Important:** After using this approach, verify components were added by listing them:
+```bash
+pac solution list-components --solutionUniqueName <UniqueName> --environment <url>
+```
+
+If the header was misspelled or the solution doesn't exist, components will be created in the default solution instead — silently. Always verify.
+
 ## Find the Solution Name
 
 Before exporting, confirm the exact unique name:
PATCH

echo "Gold patch applied."
