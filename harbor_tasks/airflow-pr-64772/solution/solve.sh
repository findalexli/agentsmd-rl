#!/bin/bash
# Gold solution for airflow-external-link-security task
# Applies the fix from apache/airflow#64772

set -e

cd /workspace/airflow

# Check if already applied (idempotency)
if grep -q 'rel="noopener noreferrer"' airflow-core/src/airflow/ui/src/pages/Connections/NothingFoundInfo.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/airflow-core/src/airflow/ui/src/pages/Connections/NothingFoundInfo.tsx b/airflow-core/src/airflow/ui/src/pages/Connections/NothingFoundInfo.tsx
index 1234567..abcdefg 100644
--- a/airflow-core/src/airflow/ui/src/pages/Connections/NothingFoundInfo.tsx
+++ b/airflow-core/src/airflow/ui/src/pages/Connections/NothingFoundInfo.tsx
@@ -36,7 +36,7 @@ export const NothingFoundInfo = () => {
         <Text>{translate("connections.nothingFound.description")}</Text>
         <Text>
           {translate("connections.nothingFound.learnMore")}{" "}
-          <Link href={docsLink} target="blank">
+          <Link href={docsLink} rel="noopener noreferrer" target="_blank">
             {translate("connections.nothingFound.documentationLink")}
           </Link>
         </Text>
PATCH

echo "Patch applied successfully"
