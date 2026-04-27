#!/usr/bin/env bash
set -euo pipefail

cd /workspace/github-copilot-for-azure

# Idempotency guard
if grep -qF "MCP tools are used exclusively for **blob discovery** \u2014 finding which blob paths" ".github/skills/analyze-skill-issues/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/analyze-skill-issues/SKILL.md b/.github/skills/analyze-skill-issues/SKILL.md
@@ -4,18 +4,18 @@ description: "Query the integration-test storage account to find why a specific
 license: MIT
 metadata:
   author: Microsoft
-  version: "1.0.0"
+  version: "1.0.1"
 ---
 
 # Analyze Skill Issues
 
-Queries the `strdashboardcejwwk` Azure Storage account that stores all integration test results and retrieves error details for a given skill.
+Queries the `strdashboarddevveobvk` Azure Storage account that stores all integration test results and retrieves error details for a given skill.
 
 ## Quick Reference
 
 | Property | Value |
 |----------|-------|
-| Storage account | `strdashboardcejwwk` |
+| Storage account | `strdashboarddevveobvk` |
 | Container | `integration-reports` |
 | Blob path pattern | `{date}/{run_id}/{skill_name}/[{test_name}/]<file>` — see [Blob Path Layout](references/blob-structure.md#blob-path-layout) |
 | **Blob discovery** | `mcp_azure_mcp_storage_blob_get` — list blobs to find the right paths |
@@ -37,7 +37,7 @@ Resolve the user's skill name to its canonical directory name using the [Skill N
 
 ## MCP Tools
 
-MCP tools are used exclusively for **blob discovery** — finding which blob paths exist. All calls require `account: "strdashboardcejwwk"` and `container: "integration-reports"`. Use `az storage blob download` (see Phase 2) to read blob content.
+MCP tools are used exclusively for **blob discovery** — finding which blob paths exist. All calls require `account: "strdashboarddevveobvk"` and `container: "integration-reports"`. Use `az storage blob download` (see Phase 2) to read blob content.
 
 | Tool | Purpose | Key parameters |
 |------|---------|----------------|
@@ -66,7 +66,7 @@ Every response **MUST** include all of the following. Do not omit any item:
 
 2. List all blobs in the container to discover available date/run paths:
    ```javascript
-   mcp_azure_mcp_storage_blob_get({ account: "strdashboardcejwwk", container: "integration-reports" })
+   mcp_azure_mcp_storage_blob_get({ account: "strdashboarddevveobvk", container: "integration-reports" })
    ```
    This returns a flat list of all blob names. Filter for entries that:
    - Start with a date string matching `yyyy-mm-dd` within the last **7 days**
@@ -82,7 +82,7 @@ Every response **MUST** include all of the following. Do not omit any item:
 For each matching blob path identified in Phase 1, download it to a local temp file and read its content:
 
 ```powershell
-az storage blob download --account-name strdashboardcejwwk --container-name integration-reports `
+az storage blob download --account-name strdashboarddevveobvk --container-name integration-reports `
   --name "<full-blob-path>" --file "$env:TEMP\<filename>" --auth-mode login --no-progress
 ```
 
@@ -153,7 +153,7 @@ See [Blob Path Layout](references/blob-structure.md#blob-path-layout) for the fu
 | Error | Cause | Remediation |
 |-------|-------|-------------|
 | No blobs found for skill | Skill has not run tests recently, or name is wrong | Verify skill name using the mapping table; tests run Tue–Sat on a schedule |
-| Blob list is empty | Container access issue or wrong account | Confirm `account: "strdashboardcejwwk"` and that the user has Azure CLI credentials |
+| Blob list is empty | Container access issue or wrong account | Confirm `account: "strdashboarddevveobvk"` and that the user has Azure CLI credentials |
 | Blob content not readable | File is binary or corrupted | Skip that blob and try adjacent blobs for the same test |
 | All tests show as skipped | The skill's test schedule hasn't run yet today | Check `tests/skills.json` for the skill's schedule and check a prior day's date prefix |
 | `token-usage.json` / `agent-metadata.json` only | Correct path but no result files | The test run may have crashed before writing results; check the run ID in GitHub Actions |
PATCH

echo "Gold patch applied."
