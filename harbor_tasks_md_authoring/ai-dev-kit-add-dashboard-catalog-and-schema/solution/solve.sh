#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-dev-kit

# Idempotency guard
if grep -qF "| **Hardcoded catalog in dashboard** | Use dataset_catalog parameter (CLI v0.281" "databricks-skills/asset-bundles/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/databricks-skills/asset-bundles/SKILL.md b/databricks-skills/asset-bundles/SKILL.md
@@ -61,13 +61,17 @@ targets:
 
 ### Dashboard Resources
 
+**Support for dataset_catalog and dataset_schema parameters added in Databricks CLI 0.281.0  (January 2026)**
+
 ```yaml
 resources:
   dashboards:
     dashboard_name:
       display_name: "[${bundle.target}] Dashboard Title"
       file_path: ../src/dashboards/dashboard.lvdash.json  # Relative to resources/
       warehouse_id: ${var.warehouse_id}
+      dataset_catalog: ${var.catalog} # Default catalog used by all datasets in the dashboard if not otherwise specified in the query
+      dataset_schema: ${var.schema} # Default schema used by all datasets in the dashboard if not otherwise specified in the query
       permissions:
         - level: CAN_RUN
           group_name: "users"
@@ -289,7 +293,7 @@ databricks bundle destroy -t prod --auto-approve
 | **Catalog doesn't exist** | Create catalog first or update variable |
 | **"admins" group error on jobs** | Cannot modify admins permissions on jobs |
 | **Volume permissions** | Use `grants` not `permissions` for volumes |
-| **Hardcoded catalog in dashboard** | Create environment-specific files or parameterize JSON |
+| **Hardcoded catalog in dashboard** | Use dataset_catalog parameter (CLI v0.281.0+), create environment-specific files, or parameterize JSON |
 | **App not starting after deploy** | Apps require `databricks bundle run <resource_key>` to start |
 | **App env vars not working** | Environment variables go in `app.yaml` (source dir), not databricks.yml |
 | **Wrong app source path** | Use `../` from resources/ dir if source is in project root |
PATCH

echo "Gold patch applied."
