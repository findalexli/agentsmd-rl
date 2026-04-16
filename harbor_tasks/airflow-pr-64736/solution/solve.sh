#!/bin/bash
# Gold solution for airflow-dagversion-select-filter
set -e

cd /workspace/airflow

# Check if already applied (idempotency)
if grep -q "useDagRunServiceGetDagRun" airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply --verbose <<'PATCH'
diff --git a/airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx b/airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx
index 95d9b8870fdc4..5ec0f97eb4890 100644
--- a/airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx
+++ b/airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx
@@ -20,7 +20,7 @@ import { createListCollection, Flex, Select, type SelectValueChangeDetails, Text
 import { useTranslation } from "react-i18next";
 import { useParams, useSearchParams } from "react-router-dom";

-import { useDagVersionServiceGetDagVersions } from "openapi/queries";
+import { useDagRunServiceGetDagRun, useDagVersionServiceGetDagVersions } from "openapi/queries";
 import type { DagVersionResponse } from "openapi/requests/types.gen";
 import { SearchParamsKeys } from "src/constants/searchParams";
 import useSelectedVersion from "src/hooks/useSelectedVersion";
@@ -34,14 +34,27 @@ type VersionSelected = {

 export const DagVersionSelect = ({ showLabel = true }: { readonly showLabel?: boolean }) => {
   const { t: translate } = useTranslation("components");
-  const { dagId = "" } = useParams();
+  const { dagId = "", runId } = useParams();
   const { data, isLoading } = useDagVersionServiceGetDagVersions({ dagId, orderBy: ["-version_number"] });
+  const { data: runData } = useDagRunServiceGetDagRun({ dagId, dagRunId: runId ?? "" }, undefined, {
+    enabled: Boolean(runId),
+  });
   const [searchParams, setSearchParams] = useSearchParams();
   const selectedVersionNumber = useSelectedVersion();
-  const selectedVersion = data?.dag_versions.find((dv) => dv.version_number === selectedVersionNumber);
+
+  // When a DagRun is selected, show only that run's versions. Otherwise, show all versions.
+  const allVersions = data?.dag_versions ?? [];
+  const versions: Array<DagVersionResponse> =
+    runId !== undefined && runData
+      ? [...runData.dag_versions].sort(
+          (versionA, versionB) => versionB.version_number - versionA.version_number,
+        )
+      : allVersions;
+
+  const selectedVersion = versions.find((dv) => dv.version_number === selectedVersionNumber);

   const versionOptions = createListCollection({
-    items: (data?.dag_versions ?? []).map((dv) => ({ value: dv.version_number, version: dv })),
+    items: versions.map((dv) => ({ value: dv.version_number, version: dv })),
   });

   const handleStateChange = ({ items }: SelectValueChangeDetails<VersionSelected>) => {
@@ -55,7 +68,7 @@ export const DagVersionSelect = ({ showLabel = true }: { readonly showLabel?: bo
     <Select.Root
       collection={versionOptions}
       data-testid="dag-run-select"
-      disabled={isLoading || !data?.dag_versions}
+      disabled={isLoading || versions.length === 0}
       onValueChange={handleStateChange}
       size="sm"
       value={selectedVersionNumber === undefined ? [] : [selectedVersionNumber.toString()]}
PATCH

echo "Gold patch applied successfully"
