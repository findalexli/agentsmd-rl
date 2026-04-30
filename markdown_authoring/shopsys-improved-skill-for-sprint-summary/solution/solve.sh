#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shopsys

# Idempotency guard
if grep -qF "**Required:** when Playwright MCP is available, generate screenshots for UX-rele" ".agents/skills/sprint-summary/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/sprint-summary/SKILL.md b/.agents/skills/sprint-summary/SKILL.md
@@ -17,6 +17,10 @@ I am ready to generate a sprint summary. Please provide:
 
 Example: /sprint-summary /home/user/jira-export.csv
 
+You can generate the CSV here: https://shopsys.atlassian.net/issues/?filter=12564
+Before exporting, update the sprint number in the filter to the sprint you want to summarize.
+To export the CSV, click the three dots in the top right corner and select "Export" -> "CSV - filter fields".
+
 Expected CSV columns:
 - Issue key (e.g., SSP-3614)
 - Summary
@@ -183,6 +187,8 @@ For each task:
 
 After the markdown is generated, check whether Playwright MCP/browser tools are available and whether the application is reachable.
 
+**Required:** when Playwright MCP is available, generate screenshots for UX-relevant tickets as part of the workflow (do not wait for a separate prompt). Default target URL is the review environment `https://<release-branch>.odin.shopsys.cloud/` (e.g. `19-0.odin.shopsys.cloud` for branch `19.0`); confirm or override with the user before starting.
+
 If yes, explicitly ask the user whether they want visual attachments for relevant tasks:
 - The user may name concrete Jira tickets
 - Or the user may let the agent choose relevant tasks
@@ -245,6 +251,20 @@ Statistics:
 Would you like to open the file in PhpStorm?
 ```
 
+5. After the user decides whether to open the file in PhpStorm, instruct them to create the article in Confluence:
+
+```
+Please create the article in Confluence here:
+https://shopsys.atlassian.net/wiki/spaces/PRG/folder/2698510337?atlOrigin=eyJpIjoiMTIzN2EwNmQyYzMyNGFiY2I1OTU1YmVkMjk4YTk1MTciLCJwIjoiYyJ9
+```
+
+6. Always include the following link with instructions for sending the summary to the maillist:
+
+```
+For instructions on sending this summary to the maillist, see:
+https://docs.google.com/document/d/172xIeT30FWxKYBh-ZedV5CRxsCv86ZkXMPdiyDuE0jU/edit?pli=1&tab=t.0
+```
+
 ## Rules for Describing Changes
 
 1. **Write in Czech** - the entire article including technical terms (where it makes sense)
PATCH

echo "Gold patch applied."
