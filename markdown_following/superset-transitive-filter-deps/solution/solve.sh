#!/usr/bin/env bash
# Apply the gold patch from apache/superset#39504.
# Idempotent: re-running this script is a no-op once the patch is applied.
set -euo pipefail

cd /workspace/superset

# Idempotency guard — a unique token from the patch.
if grep -q "resolveTransitiveParentIds" \
    superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/state.ts \
    2>/dev/null; then
    echo "Gold patch already applied — nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterValue.tsx b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterValue.tsx
index f2ee5fc5acff..9d552b91b3b2 100644
--- a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterValue.tsx
+++ b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterValue.tsx
@@ -61,7 +61,7 @@ import { RESPONSIVE_WIDTH } from 'src/filters/components/common';
 import { dispatchHoverAction, dispatchFocusAction } from './utils';
 import { FilterControlProps } from './types';
 import { getFormData } from '../../utils';
-import { useFilterDependencies } from './state';
+import { useFilterDependencies, useTransitiveParentIds } from './state';
 import { useFilterOutlined } from '../useFilterOutlined';

 const HEIGHT = 32;
@@ -119,6 +119,7 @@ const FilterValue: FC<FilterValueProps> = ({
   const granularitySqla = isCustomization ? undefined : filter.granularity_sqla;
   const metadata = getChartMetadataRegistry().get(filterType);
   const dependencies = useFilterDependencies(id, dataMaskSelected);
+  const transitiveParentIds = useTransitiveParentIds(id);
   const shouldRefresh = useShouldFilterRefresh();

   const behaviors = useMemo(
@@ -187,12 +188,15 @@ const FilterValue: FC<FilterValueProps> = ({
       dashboardId,
     });
     const filterOwnState = filter.dataMask?.ownState || {};
-    if ((filter.cascadeParentIds ?? []).length) {
-      // Prevent unnecessary backend requests by validating parent filter selections first
+    if (transitiveParentIds.length) {
+      // Prevent unnecessary backend requests by validating ancestor filter
+      // selections first. We walk the full transitive ancestor chain (not just
+      // direct parents) so the counts line up with `dependencies`, which is
+      // itself built from the transitive chain by `useFilterDependencies`.

       let selectedParentFilterValueCounts = 0;
       let isTimeRangeSelected = false;
-      (filter.cascadeParentIds ?? []).forEach(pId => {
+      transitiveParentIds.forEach(pId => {
         const extraFormData = dataMaskSelected?.[pId]?.extraFormData;
         if (extraFormData?.filters?.length) {
           selectedParentFilterValueCounts += extraFormData.filters.length;
@@ -202,7 +206,7 @@ const FilterValue: FC<FilterValueProps> = ({
         }
       });

-      // check if all parent filters with defaults have a value selected
+      // check if all ancestor filters with defaults have a value selected

       const depsCount = dependencies.filters?.length ?? 0;
       const hasTimeRangeDeps = Boolean(dependencies?.time_range);
@@ -212,7 +216,7 @@ const FilterValue: FC<FilterValueProps> = ({
         (hasTimeRangeDeps && !isTimeRangeSelected)
       ) {
         // child filter should not request backend until it
-        // has all the required information from parent filters
+        // has all the required information from ancestor filters
         return;
       }
       setHasDepsFilterValue(false);
@@ -291,6 +295,7 @@ const FilterValue: FC<FilterValueProps> = ({
     shouldRefresh,
     dataMaskSelected,
     setHasDepsFilterValue,
+    transitiveParentIds,
   ]);

   useEffect(() => {
diff --git a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/state.ts b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/state.ts
index bb5b5c2672e2..37d5e809256b 100644
--- a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/state.ts
+++ b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/state.ts
@@ -18,25 +18,41 @@
  */
 import { useMemo } from 'react';
 import { shallowEqual, useSelector } from 'react-redux';
-import {
-  DataMaskStateWithId,
-  ensureIsArray,
-  ExtraFormData,
-} from '@superset-ui/core';
+import { DataMaskStateWithId, ExtraFormData } from '@superset-ui/core';
+import { RootState } from 'src/dashboard/types';
 import { mergeExtraFormData } from '../../utils';
+import {
+  FilterConfigMap,
+  resolveTransitiveParentIds,
+} from '../../dependencyGraph';
+
+/**
+ * Resolve the transitive ancestor ids for a given filter from the live
+ * native-filter configuration in Redux. Shared between
+ * `useFilterDependencies` and the readiness guard in `FilterValue` so they
+ * always agree on which parents count.
+ */
+export function useTransitiveParentIds(id: string): string[] {
+  const filterConfig = useSelector<RootState, FilterConfigMap | undefined>(
+    state => state.nativeFilters?.filters,
+    shallowEqual,
+  );
+
+  return useMemo(
+    () => resolveTransitiveParentIds(id, filterConfig ?? {}),
+    [id, filterConfig],
+  );
+}

-// eslint-disable-next-line import/prefer-default-export
 export function useFilterDependencies(
   id: string,
   dataMaskSelected?: DataMaskStateWithId,
 ): ExtraFormData {
-  const dependencyIds = useSelector<any, string[] | undefined>(
-    state => state.nativeFilters.filters[id]?.cascadeParentIds,
-    shallowEqual,
-  );
+  const dependencyIds = useTransitiveParentIds(id);
+
   return useMemo(() => {
-    let dependencies = {};
-    ensureIsArray(dependencyIds).forEach(parentId => {
+    let dependencies: ExtraFormData = {};
+    dependencyIds.forEach(parentId => {
       const parentState = dataMaskSelected?.[parentId];
       dependencies = mergeExtraFormData(
         dependencies,
diff --git a/superset-frontend/src/dashboard/components/nativeFilters/dependencyGraph.ts b/superset-frontend/src/dashboard/components/nativeFilters/dependencyGraph.ts
new file mode 100644
index 000000000000..e4232524d77d
--- /dev/null
+++ b/superset-frontend/src/dashboard/components/nativeFilters/dependencyGraph.ts
@@ -0,0 +1,75 @@
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
+import { ensureIsArray } from '@superset-ui/core';
+
+/**
+ * Shared graph primitives for the native-filter dependency graph.
+ *
+ * A dependent filter stores only its *direct* parents in `cascadeParentIds`,
+ * but most consumers (options queries, `extra_form_data` emitted to charts,
+ * readiness checks) need the full transitive ancestor set. Keeping the graph
+ * primitives here lets the hook layer and any non-React callers (e.g. form
+ * validation, batch checks) share one traversal implementation.
+ */
+
+/**
+ * Minimal shape we need from the native-filter config map. Kept intentionally
+ * narrow so dividers / chart customizations (which may omit `cascadeParentIds`)
+ * are also assignable.
+ */
+export type FilterConfigMap = Record<string, { cascadeParentIds?: string[] }>;
+
+/**
+ * Resolve the full set of transitive ancestor filter ids for the given filter,
+ * in topological order (furthest ancestor first, closest parent last).
+ *
+ * The ordering is significant: `mergeExtraFormData` appends filter arrays but
+ * *overrides* scalar fields like `time_range`, so iterating ancestors from
+ * furthest to closest makes the closest parent's scalar overrides win. A chain
+ * A -> B -> C -> D where each level lists only its direct parent therefore
+ * produces `[A, B, C]` for D, which matches the intended precedence.
+ *
+ * Cycles are silently skipped. The filter-config modal enforces acyclicity at
+ * save time (see `hasCircularDependency`), but defensive traversal here keeps
+ * a malformed saved config from spinning forever.
+ */
+export function resolveTransitiveParentIds(
+  id: string,
+  filterConfig: FilterConfigMap,
+): string[] {
+  const ordered: string[] = [];
+  const visited = new Set<string>([id]);
+
+  const visit = (currentId: string) => {
+    const parents = ensureIsArray(
+      filterConfig[currentId]?.cascadeParentIds,
+    ) as string[];
+    parents.forEach(parentId => {
+      if (visited.has(parentId)) return;
+      visited.add(parentId);
+      // Depth-first so the furthest ancestors are appended before the
+      // closer parents, giving a stable topological order.
+      visit(parentId);
+      ordered.push(parentId);
+    });
+  };
+
+  visit(id);
+  return ordered;
+}
PATCH

echo "Gold patch applied."
