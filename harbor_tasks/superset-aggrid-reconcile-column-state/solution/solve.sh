#!/bin/bash
# Apply the gold patch for apache/superset#39333. Idempotent: if the
# distinctive marker is already present, do nothing.
set -euo pipefail

cd /workspace/superset

MARKER='import reconcileColumnState from '\''../utils/reconcileColumnState'\'';'
TARGET='superset-frontend/plugins/plugin-chart-ag-grid-table/src/AgGridTable/index.tsx'

if grep -qF "$MARKER" "$TARGET"; then
    echo "patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/plugins/plugin-chart-ag-grid-table/src/AgGridTable/index.tsx b/superset-frontend/plugins/plugin-chart-ag-grid-table/src/AgGridTable/index.tsx
index 011c2cf0ef9f..4b6bd9e276f5 100644
--- a/superset-frontend/plugins/plugin-chart-ag-grid-table/src/AgGridTable/index.tsx
+++ b/superset-frontend/plugins/plugin-chart-ag-grid-table/src/AgGridTable/index.tsx
@@ -56,6 +56,7 @@ import SearchSelectDropdown from './components/SearchSelectDropdown';
 import { SearchOption, SortByItem } from '../types';
 import getInitialSortState, { shouldSort } from '../utils/getInitialSortState';
 import getInitialFilterModel from '../utils/getInitialFilterModel';
+import reconcileColumnState from '../utils/reconcileColumnState';
 import { PAGE_SIZE_OPTIONS } from '../consts';
 import { getCompleteFilterState } from '../utils/filterStateManager';

@@ -429,10 +430,17 @@ const AgGridDataTable: FunctionComponent<AgGridTableProps> = memo(
       // Note: filterModel is now handled via gridInitialState for better performance
       if (chartState?.columnState && params.api) {
         try {
-          params.api.applyColumnState?.({
-            state: chartState.columnState as ColumnState[],
-            applyOrder: true,
-          });
+          const reconciledColumnState = reconcileColumnState(
+            chartState.columnState as ColumnState[],
+            colDefsFromProps as ColDef[],
+          );
+
+          if (reconciledColumnState) {
+            params.api.applyColumnState?.({
+              state: reconciledColumnState.columnState,
+              applyOrder: reconciledColumnState.applyOrder,
+            });
+          }
         } catch {
           // Silently fail if state restoration fails
         }
diff --git a/superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.test.ts b/superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.test.ts
new file mode 100644
index 000000000000..78e0e79b2dad
--- /dev/null
+++ b/superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.test.ts
@@ -0,0 +1,86 @@
+/**
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
+import {
+  type ColDef,
+  type ColumnState,
+} from '@superset-ui/core/components/ThemedAgGridReact';
+import reconcileColumnState, { getLeafColumnIds } from './reconcileColumnState';
+
+test('getLeafColumnIds flattens grouped column defs in visual order', () => {
+  const colDefs: ColDef[] = [
+    { field: 'Manufacture_Date' },
+    {
+      headerName: 'Metrics',
+      children: [
+        { field: 'SUM(Sales_Amount)' },
+        { field: 'SUM(Discount_Applied)' },
+      ],
+    } as ColDef,
+    { field: 'SUM(Quantity_Sold)' },
+  ];
+
+  expect(getLeafColumnIds(colDefs)).toEqual([
+    'Manufacture_Date',
+    'SUM(Sales_Amount)',
+    'SUM(Discount_Applied)',
+    'SUM(Quantity_Sold)',
+  ]);
+});
+
+test('preserves saved order when the current column set is unchanged', () => {
+  const colDefs: ColDef[] = [
+    { field: 'Transaction_Timestamp' },
+    { field: 'SUM(Sales_Amount)' },
+    { field: 'SUM(Discount_Applied)' },
+  ];
+  const savedColumnState: ColumnState[] = [
+    { colId: 'SUM(Sales_Amount)' },
+    { colId: 'Transaction_Timestamp' },
+    { colId: 'SUM(Discount_Applied)' },
+  ];
+
+  expect(reconcileColumnState(savedColumnState, colDefs)).toEqual({
+    applyOrder: true,
+    columnState: savedColumnState,
+  });
+});
+
+test('drops stale order when a dynamic group by swaps the dimension column', () => {
+  const currentColDefs: ColDef[] = [
+    { field: 'Manufacture_Date' },
+    { field: 'SUM(Sales_Amount)' },
+    { field: 'SUM(Discount_Applied)' },
+    { field: 'SUM(Quantity_Sold)' },
+  ];
+  const savedColumnState: ColumnState[] = [
+    { colId: 'Transaction_Timestamp' },
+    { colId: 'SUM(Sales_Amount)' },
+    { colId: 'SUM(Discount_Applied)' },
+    { colId: 'SUM(Quantity_Sold)' },
+  ];
+
+  expect(reconcileColumnState(savedColumnState, currentColDefs)).toEqual({
+    applyOrder: false,
+    columnState: [
+      { colId: 'SUM(Sales_Amount)' },
+      { colId: 'SUM(Discount_Applied)' },
+      { colId: 'SUM(Quantity_Sold)' },
+    ],
+  });
+});
diff --git a/superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.ts b/superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.ts
new file mode 100644
index 000000000000..46577713a16e
--- /dev/null
+++ b/superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.ts
@@ -0,0 +1,83 @@
+/**
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
+import {
+  type ColDef,
+  type ColumnState,
+} from '@superset-ui/core/components/ThemedAgGridReact';
+
+type ColumnGroupDef = ColDef & {
+  children?: ColumnDefLike[];
+};
+
+type ColumnDefLike = ColDef | ColumnGroupDef;
+
+function hasChildren(colDef: ColumnDefLike): colDef is ColumnGroupDef {
+  return 'children' in colDef;
+}
+
+export interface ReconciledColumnState {
+  applyOrder: boolean;
+  columnState: ColumnState[];
+}
+
+export function getLeafColumnIds(colDefs: ColumnDefLike[]): string[] {
+  return colDefs.flatMap(colDef => {
+    if (
+      hasChildren(colDef) &&
+      Array.isArray(colDef.children) &&
+      colDef.children.length > 0
+    ) {
+      return getLeafColumnIds(colDef.children);
+    }
+
+    return typeof colDef.field === 'string' ? [colDef.field] : [];
+  });
+}
+
+export default function reconcileColumnState(
+  savedColumnState: ColumnState[] | undefined,
+  colDefs: ColumnDefLike[],
+): ReconciledColumnState | null {
+  if (!Array.isArray(savedColumnState) || savedColumnState.length === 0) {
+    return null;
+  }
+
+  const currentColumnIds = getLeafColumnIds(colDefs);
+  const currentColumnIdSet = new Set(currentColumnIds);
+  const filteredColumnState = savedColumnState.filter(
+    column =>
+      typeof column.colId === 'string' && currentColumnIdSet.has(column.colId),
+  );
+
+  if (filteredColumnState.length === 0) {
+    return null;
+  }
+
+  const savedColumnIdSet = new Set(
+    filteredColumnState.map(column => column.colId),
+  );
+  const hasSameColumnSet =
+    currentColumnIds.length === savedColumnIdSet.size &&
+    currentColumnIds.every(columnId => savedColumnIdSet.has(columnId));
+
+  return {
+    columnState: filteredColumnState,
+    applyOrder: hasSameColumnSet,
+  };
+}
PATCH

echo "patch applied"
