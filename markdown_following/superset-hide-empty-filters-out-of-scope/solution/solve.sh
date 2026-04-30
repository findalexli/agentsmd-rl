#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

if grep -q "showFiltersOutOfScope" superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.tsx 2>/dev/null; then
    echo "Gold patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.test.tsx b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.test.tsx
index 9f4c6e8ed2a6..935928bada06 100644
--- a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.test.tsx
+++ b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.test.tsx
@@ -384,6 +384,19 @@ test('FilterControls should handle empty filters list', () => {
   expect(container).toBeInTheDocument();
 });

+test('does not render "Filters out of scope" when all filters are in scope', () => {
+  const state = getDefaultState(FilterBarOrientation.Vertical);
+
+  const { useSelector } = jest.requireMock('react-redux');
+  useSelector.mockImplementation((selector: (s: typeof state) => unknown) =>
+    selector(state),
+  );
+
+  setupWithFilters(state);
+
+  expect(screen.queryByText(/Filters out of scope/)).not.toBeInTheDocument();
+});
+
 test('FilterControls overflowedByIndex updates when filters change scope', () => {
   const state = getDefaultState(FilterBarOrientation.Vertical);

diff --git a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.tsx b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.tsx
index 35efda046231..ac235b153204 100644
--- a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.tsx
+++ b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.tsx
@@ -222,6 +222,11 @@ const FilterControls: FC<FilterControlsProps> = ({
     chartCustomization: true,
   });

+  const showFiltersOutOfScope =
+    showCollapsePanel &&
+    (hideHeader || sectionsOpen.filters) &&
+    filtersOutOfScope.length > 0;
+
   const toggleSection = useCallback((section: keyof typeof sectionsOpen) => {
     setSectionsOpen(prev => ({
       ...prev,
@@ -343,7 +348,7 @@ const FilterControls: FC<FilterControlsProps> = ({
           </SectionContainer>
         )}

-        {showCollapsePanel && (hideHeader || sectionsOpen.filters) && (
+        {showFiltersOutOfScope && (
           <FiltersOutOfScopeCollapsible
             filtersOutOfScope={filtersOutOfScope}
             renderer={renderer}
diff --git a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/FiltersDropdownContent.test.tsx b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/FiltersDropdownContent.test.tsx
new file mode 100644
index 000000000000..04cf8e192fc5
--- /dev/null
+++ b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/FiltersDropdownContent.test.tsx
@@ -0,0 +1,71 @@
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
+import { render, screen } from 'spec/helpers/testing-library';
+import { Filter } from '@superset-ui/core';
+import { FiltersDropdownContent } from '.';
+
+const buildFilter = (id: string, name: string): Filter =>
+  ({
+    id,
+    name,
+    filterType: 'filter_select',
+    targets: [{ datasetId: 1, column: { name: 'country' } }],
+    defaultDataMask: {},
+    controlValues: {},
+    cascadeParentIds: [],
+    scope: { rootPath: ['ROOT_ID'], excluded: [] as string[] },
+  }) as unknown as Filter;
+
+const baseProps = {
+  overflowedCrossFilters: [],
+  filtersInScope: [buildFilter('filter-1', 'In Scope Filter')],
+  renderer: (filter: any) => <div key={filter.id}>{filter.name}</div>,
+  rendererCrossFilter: () => null,
+  showCollapsePanel: true,
+  forceRenderOutOfScope: false,
+};
+
+test('does not render "Filters out of scope" section when filtersOutOfScope is empty', () => {
+  render(<FiltersDropdownContent {...baseProps} filtersOutOfScope={[]} />);
+
+  expect(screen.queryByText(/Filters out of scope/)).not.toBeInTheDocument();
+});
+
+test('renders "Filters out of scope" section when one or more filters are out of scope', () => {
+  render(
+    <FiltersDropdownContent
+      {...baseProps}
+      filtersOutOfScope={[buildFilter('filter-2', 'Out of Scope Filter')]}
+    />,
+  );
+
+  expect(screen.getByText(/Filters out of scope/)).toBeInTheDocument();
+});
+
+test('does not render "Filters out of scope" section when showCollapsePanel is false', () => {
+  render(
+    <FiltersDropdownContent
+      {...baseProps}
+      showCollapsePanel={false}
+      filtersOutOfScope={[buildFilter('filter-2', 'Out of Scope Filter')]}
+    />,
+  );
+
+  expect(screen.queryByText(/Filters out of scope/)).not.toBeInTheDocument();
+});
diff --git a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/index.tsx b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/index.tsx
index 07c3696eb8fc..5900a9ec6e58 100644
--- a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/index.tsx
+++ b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/index.tsx
@@ -61,7 +61,7 @@ export const FiltersDropdownContent = ({
       ),
     )}
     {filtersInScope.map(renderer)}
-    {showCollapsePanel && (
+    {showCollapsePanel && filtersOutOfScope.length > 0 && (
       <FiltersOutOfScopeCollapsible
         filtersOutOfScope={filtersOutOfScope}
         renderer={renderer}
diff --git a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersOutOfScopeCollapsible/index.tsx b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersOutOfScopeCollapsible/index.tsx
index 7c9a22629074..43d4edec9b13 100644
--- a/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersOutOfScopeCollapsible/index.tsx
+++ b/superset-frontend/src/dashboard/components/nativeFilters/FilterBar/FiltersOutOfScopeCollapsible/index.tsx
@@ -37,7 +37,6 @@ export const FiltersOutOfScopeCollapsible = ({
     ghost
     bordered
     expandIconPosition="end"
-    collapsible={filtersOutOfScope.length === 0 ? 'disabled' : undefined}
     items={[
       {
         key: 'out-of-scope-filters',
PATCH

echo "Gold patch applied successfully."
