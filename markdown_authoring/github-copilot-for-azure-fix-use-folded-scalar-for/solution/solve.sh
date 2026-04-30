#!/usr/bin/env bash
set -euo pipefail

cd /workspace/github-copilot-for-azure

# Idempotency guard
if grep -qF "Plain unquoted descriptions with `: ` patterns (e.g., `USE FOR:`, `Azure AI:`) c" ".github/skills/sensei/references/SCORING.md" && grep -qF "Azure Observability Services including Azure Monitor, Application Insights, Log " "plugin/skills/azure-observability/SKILL.md" && grep -qF "Create new Azure Database for PostgreSQL Flexible Server instances and configure" "plugin/skills/azure-postgres/SKILL.md" && grep -qF "Azure Storage Services including Blob Storage, File Shares, Queue Storage, Table" "plugin/skills/azure-storage/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/sensei/references/SCORING.md b/.github/skills/sensei/references/SCORING.md
@@ -219,6 +219,27 @@ Per the spec, SKILL.md should follow progressive disclosure:
 
 **Line count check:** The spec recommends keeping SKILL.md under 500 lines. Report a warning if exceeded.
 
+### 8. YAML Description Safety
+
+Descriptions containing YAML special characters (especially `: ` colon-space) **must** use either:
+- Folded scalar (`>-`) — **preferred** for descriptions > 200 chars
+- Double-quoted string (`"..."`) — acceptable alternative
+
+Plain unquoted descriptions with `: ` patterns (e.g., `USE FOR:`, `Azure AI:`) cause YAML parse errors in many skill loaders:
+```
+Nested mappings are not allowed in compact mappings
+```
+
+| Check | Pass | Fail |
+|-------|------|------|
+| Uses `>-` or `"..."` | `description: >-` | `description: Use for Azure AI: Search...` |
+| No `: ` in plain value | `description: Simple text here` | `description: USE FOR: something` |
+| Over 200 chars uses `>-` | `description: >-` (multi-line) | `description: Very long plain text...` |
+
+**Scoring impact:**
+- Plain description with `: ` → **Invalid** (will fail to parse)
+- Description > 200 chars without `>-` → **Warning** (maintainability concern)
+
 ---
 
 ## Scoring Algorithm
@@ -230,6 +251,11 @@ function scoreSkill(skill):
         report "INVALID: name fails spec validation"
         return "Invalid"
     
+    # Check YAML description safety
+    if isPlainUnquoted(skill.rawDescription) AND contains(skill.description, ": "):
+        report "INVALID: plain description contains ': ' — use >- or quotes"
+        return "Invalid"
+    
     score = "Low"
     
     # Check description length
@@ -273,6 +299,8 @@ function collectSuggestions(skill):
         suggestions.add("Add license field (e.g., license: MIT)")
     if skill.metadata == null OR skill.metadata.version == null:
         suggestions.add("Add metadata.version field (e.g., metadata: { version: \"1.0\" })")
+    if isPlainUnquoted(skill.rawDescription) AND skill.description.length > 200:
+        suggestions.add("Use >- folded scalar for description (over 200 chars)")
     return suggestions
 ```
 
diff --git a/plugin/skills/azure-observability/SKILL.md b/plugin/skills/azure-observability/SKILL.md
@@ -1,6 +1,9 @@
 ---
 name: azure-observability
-description: Azure Observability Services including Azure Monitor, Application Insights, Log Analytics, Alerts, and Workbooks. Provides metrics, APM, distributed tracing, KQL queries, and interactive reports.
+description: >-
+  Azure Observability Services including Azure Monitor, Application Insights, Log Analytics, Alerts, and Workbooks. Provides metrics, APM, distributed tracing, KQL queries, and interactive reports.
+  USE FOR: Azure Monitor, Application Insights, Log Analytics, Alerts, Workbooks, metrics, APM, distributed tracing, KQL queries, interactive reports, observability, monitoring dashboards.
+  DO NOT USE FOR: instrumenting apps with App Insights SDK (use appinsights-instrumentation), querying Kusto/ADX clusters (use azure-kusto), cost analysis (use azure-cost-optimization).
 ---
 
 # Azure Observability Services
diff --git a/plugin/skills/azure-postgres/SKILL.md b/plugin/skills/azure-postgres/SKILL.md
@@ -1,6 +1,9 @@
 ---
 name: azure-postgres
-description: Create new Azure Database for PostgreSQL Flexible Server instances and configure passwordless authentication with Microsoft Entra ID. Set up developer access, managed identities for apps, group-based permissions, and migrate from password-based to Entra ID authentication. Trigger phrases include "passwordless for postgres", "entra id postgres", "azure ad postgres authentication", "postgres managed identity", "migrate postgres to passwordless".
+description: >-
+  Create new Azure Database for PostgreSQL Flexible Server instances and configure passwordless authentication with Microsoft Entra ID. Set up developer access, managed identities for apps, group-based permissions, and migrate from password-based to Entra ID authentication.
+  USE FOR: passwordless for postgres, entra id postgres, azure ad postgres authentication, postgres managed identity, migrate postgres to passwordless, create postgres server, configure postgres auth.
+  DO NOT USE FOR: MySQL databases (use azure-prepare), Cosmos DB (use azure-prepare), general Azure resource creation (use azure-prepare).
 ---
 
 # Azure Database for PostgreSQL
diff --git a/plugin/skills/azure-storage/SKILL.md b/plugin/skills/azure-storage/SKILL.md
@@ -1,6 +1,9 @@
 ---
 name: azure-storage
-description: Azure Storage Services including Blob Storage, File Shares, Queue Storage, Table Storage, and Data Lake. Provides object storage, SMB file shares, async messaging, NoSQL key-value, and big data analytics capabilities. Includes access tiers (hot, cool, archive) and lifecycle management.
+description: >-
+  Azure Storage Services including Blob Storage, File Shares, Queue Storage, Table Storage, and Data Lake. Provides object storage, SMB file shares, async messaging, NoSQL key-value, and big data analytics capabilities. Includes access tiers (hot, cool, archive) and lifecycle management.
+  USE FOR: blob storage, file shares, queue storage, table storage, data lake, upload files, download blobs, storage accounts, access tiers, lifecycle management.
+  DO NOT USE FOR: SQL databases (use azure-postgres), Cosmos DB (use azure-prepare), messaging with Event Hubs or Service Bus (use azure-messaging).
 ---
 
 # Azure Storage Services
PATCH

echo "Gold patch applied."
