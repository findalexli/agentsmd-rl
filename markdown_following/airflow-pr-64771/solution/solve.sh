#!/bin/bash
# Gold solution - apply the fix for DagVersionSelect filtering
set -e

cd /workspace/airflow

# Idempotency check - skip if patch already applied
if grep -q "useDagRunServiceGetDagRun" airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch (component fix + test file)
patch -p1 <<'PATCH'
diff --git a/airflow-core/src/airflow/ui/src/components/DagVersionSelect.test.tsx b/airflow-core/src/airflow/ui/src/components/DagVersionSelect.test.tsx
new file mode 100644
index 0000000000000..38b0332252aeb
--- /dev/null
+++ b/airflow-core/src/airflow/ui/src/components/DagVersionSelect.test.tsx
@@ -0,0 +1,120 @@
+/*!
+ * Licensed to the Apache Software Foundation (ASF) under one
+ * or more contributor license agreements.  See the NOTICE file
+ * distributed with this work for additional information
+ * regarding copyright ownership.  The ASF licenses this file
+ * to you under the Apache License, Version 2.0 (the
+ * "License"); you may not use this file except in compliance
+ * with the License.  You may obtain a copy of the License at
+ *
+ *   http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing,
+ * software distributed under the License is distributed on an
+ * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+ * KIND, either express or implied.  See the License for the
+ * specific language governing permissions and limitations
+ * under the License.
+ */
+import { render } from "@testing-library/react";
+import { describe, expect, it, vi } from "vitest";
+
+import { Wrapper } from "src/utils/Wrapper";
+
+import { DagVersionSelect } from "./DagVersionSelect";
+
+const dagVersionV1 = {
+  bundle_name: "dags-folder",
+  bundle_version: null,
+  created_at: "2025-01-01T00:00:00Z",
+  dag_id: "test_dag",
+  version_number: 1,
+};
+const dagVersionV2 = {
+  bundle_name: "dags-folder",
+  bundle_version: null,
+  created_at: "2025-01-02T00:00:00Z",
+  dag_id: "test_dag",
+  version_number: 2,
+};
+const dagVersionV3 = {
+  bundle_name: "dags-folder",
+  bundle_version: null,
+  created_at: "2025-01-03T00:00:00Z",
+  dag_id: "test_dag",
+  version_number: 3,
+};
+
+const allVersions = [dagVersionV3, dagVersionV2, dagVersionV1];
+
+let mockParams: Record<string, string> = { dagId: "test_dag" };
+
+vi.mock("react-router-dom", async () => {
+  const actual = await vi.importActual("react-router-dom");
+
+  return {
+    ...actual,
+    useParams: () => mockParams,
+  };
+});
+
+vi.mock("openapi/queries", () => ({
+  useDagRunServiceGetDagRun: vi.fn(() => ({
+    data: undefined,
+    isLoading: false,
+  })),
+  useDagVersionServiceGetDagVersions: vi.fn(() => ({
+    data: { dag_versions: allVersions, total_entries: 3 },
+    isLoading: false,
+  })),
+}));
+
+vi.mock("src/hooks/useSelectedVersion", () => ({
+  default: vi.fn(() => undefined),
+}));
+
+const { useDagRunServiceGetDagRun } = await import("openapi/queries");
+
+const mockRunData = {
+  bundle_version: null,
+  conf: null,
+  dag_display_name: "test_dag",
+  dag_id: "test_dag",
+  dag_versions: [dagVersionV1, dagVersionV2],
+  end_date: null,
+  has_missed_deadline: false,
+  logical_date: null,
+  note: null,
+  partition_key: null,
+  queued_at: null,
+  run_after: "2025-01-01T00:00:00Z",
+  run_id: "run_1",
+  run_type: "manual" as const,
+  start_date: null,
+  state: "success" as const,
+  triggered_by: "ui" as const,
+  triggering_user_name: null,
+};
+
+const getItems = (container: HTMLElement) => container.querySelectorAll(".chakra-select__item");
+
+describe("DagVersionSelect", () => {
+  it("shows all versions when no DagRun is selected", () => {
+    mockParams = { dagId: "test_dag" };
+    const { container } = render(<DagVersionSelect />, { wrapper: Wrapper });
+
+    expect(getItems(container)).toHaveLength(3);
+  });
+
+  it("shows only the selected run's versions when a DagRun is selected", () => {
+    mockParams = { dagId: "test_dag", runId: "run_1" };
+    vi.mocked(useDagRunServiceGetDagRun).mockReturnValue({
+      data: mockRunData,
+      isLoading: false,
+    } as ReturnType<typeof useDagRunServiceGetDagRun>);
+
+    const { container } = render(<DagVersionSelect />, { wrapper: Wrapper });
+
+    expect(getItems(container)).toHaveLength(2);
+  });
+});
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
