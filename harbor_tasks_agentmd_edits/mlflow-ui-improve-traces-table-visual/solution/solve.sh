#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotent: skip if already applied
if grep -q 'handleCheck' mlflow/server/js/src/shared/web-shared/genai-traces-table/components/EvaluationsOverviewColumnSelectorGrouped.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/mlflow/server/js/src/shared/web-shared/genai-traces-table/GenAITracesTable.tsx b/mlflow/server/js/src/shared/web-shared/genai-traces-table/GenAITracesTable.tsx
index e7bd4f95287cf..515a1524f21b4 100644
--- a/mlflow/server/js/src/shared/web-shared/genai-traces-table/GenAITracesTable.tsx
+++ b/mlflow/server/js/src/shared/web-shared/genai-traces-table/GenAITracesTable.tsx
@@ -27,7 +27,7 @@ import { GenAITracesTableActions } from './GenAITracesTableActions';
 import { computeEvaluationsComparison } from './GenAiTracesTable.utils';
 import { GenAiTracesTableBody } from './GenAiTracesTableBody';
 import { GenAiTracesTableSearchInput } from './GenAiTracesTableSearchInput';
-import { EvaluationsOverviewColumnSelector } from './components/EvaluationsOverviewColumnSelector';
+import { EvaluationsOverviewColumnSelectorGrouped } from './components/EvaluationsOverviewColumnSelectorGrouped';
 import { EvaluationsOverviewSortDropdown } from './components/EvaluationsOverviewSortDropdown';
 import { GenAiEvaluationBadge } from './components/GenAiEvaluationBadge';
 import {
@@ -486,10 +486,11 @@ function GenAiTracesTableImpl({
                 />

                 {/* Column selector */}
-                <EvaluationsOverviewColumnSelector
+                <EvaluationsOverviewColumnSelectorGrouped
                   columns={allColumns}
                   selectedColumns={selectedColumns}
-                  setSelectedColumnsWithHiddenColumns={toggleColumns}
+                  toggleColumns={toggleColumns}
+                  setSelectedColumns={setSelectedColumns}
                 />
                 <GenAITracesTableActions
                   experimentId={experimentId}
diff --git a/mlflow/server/js/src/shared/web-shared/genai-traces-table/components/EvaluationsOverviewColumnSelectorGrouped.tsx b/mlflow/server/js/src/shared/web-shared/genai-traces-table/components/EvaluationsOverviewColumnSelectorGrouped.tsx
index d1f4f8baad695..1402fc51e05f1 100644
--- a/mlflow/server/js/src/shared/web-shared/genai-traces-table/components/EvaluationsOverviewColumnSelectorGrouped.tsx
+++ b/mlflow/server/js/src/shared/web-shared/genai-traces-table/components/EvaluationsOverviewColumnSelectorGrouped.tsx
@@ -1,18 +1,15 @@
-import React, { useMemo, useState } from 'react';
+import React, { useMemo, useState, useCallback } from 'react';

 import {
   ChevronDownIcon,
-  DialogCombobox,
-  DialogComboboxContent,
-  DialogComboboxCustomButtonTriggerWrapper,
-  DialogComboboxOptionList,
-  DialogComboboxOptionListCheckboxItem,
-  DialogComboboxSectionHeader,
   Button,
   ColumnsIcon,
   useDesignSystemTheme,
-  DialogComboboxOptionListSearch,
   DangerIcon,
+  Dropdown,
+  Input,
+  SearchIcon,
+  Tree,
 } from '@databricks/design-system';
 import { FormattedMessage, useIntl } from '@databricks/i18n';

@@ -28,16 +25,42 @@ interface Props {
   metadataError?: Error | null;
 }

-const OPTION_HEIGHT = 32;
-
 const getGroupLabel = (group: string): string => {
   return group === TracesTableColumnGroup.INFO
     ? 'Attributes'
     : TracesTableColumnGroupToLabelMap[group as TracesTableColumnGroup];
 };

+const getGroupKey = (group: string): string => {
+  return `GROUP-${group}`;
+};
+
+/**
+ * Function dissects given string and wraps the
+ * searched query with <strong>...</strong> if found. Used for highlighting search.
+ */
+const createHighlightedNode = (value: string, filterQuery: string) => {
+  if (!filterQuery) {
+    return value;
+  }
+  const index = value.toLowerCase().indexOf(filterQuery.toLowerCase());
+  const beforeStr = value.substring(0, index);
+  const matchStr = value.substring(index, index + filterQuery.length);
+  const afterStr = value.substring(index + filterQuery.length);
+
+  return index > -1 ? (
+    <span>
+      {beforeStr}
+      <strong>{matchStr}</strong>
+      {afterStr}
+    </span>
+  ) : (
+    value
+  );
+};
+
 /**
- * Column selector with section headers for each column-group.
+ * Column selector with collapsible tree structure for each column group.
  */
 export const EvaluationsOverviewColumnSelectorGrouped: React.FC<React.PropsWithChildren<Props>> = ({
   columns = [],
@@ -51,6 +74,7 @@ export const EvaluationsOverviewColumnSelectorGrouped: React.FC<React.PropsWithC
   const { theme } = useDesignSystemTheme();

   const [search, setSearch] = useState('');
+  const [dropdownVisible, setDropdownVisible] = useState(false);

   const sortedGroupedColumns = useMemo(() => {
     const sortedColumns = sortGroupedColumns(columns);
@@ -87,60 +111,71 @@ export const EvaluationsOverviewColumnSelectorGrouped: React.FC<React.PropsWithC
     return out;
   }, [sortedGroupedColumns, search]);

-  const handleToggle = (column: TracesTableColumn) => {
-    return toggleColumns([column]);
-  };
-
-  const handleSelectAllInGroup = (groupColumns: TracesTableColumn[]) => {
-    const allSelected = groupColumns.every((col) => selectedColumns.some((c) => c.id === col.id));
-    if (allSelected) {
-      // If all are selected, deselect all in this group
-      const newSelection = selectedColumns.filter((col) => !groupColumns.some((gc) => gc.id === col.id));
-      setSelectedColumns(newSelection);
-    } else {
-      // If not all are selected, select all in this group
-      const newSelection = [...selectedColumns];
-      groupColumns.forEach((col) => {
-        if (!newSelection.some((c) => c.id === col.id)) {
-          newSelection.push(col);
+  // Build tree data structure - memoized to prevent re-creation
+  const treeData = useMemo(() => {
+    return Object.entries(filteredGroupedColumns).map(([groupName, cols]) => {
+      const groupLabel = getGroupLabel(groupName);
+      return {
+        key: getGroupKey(groupName),
+        title: `${groupLabel} (${cols.length})`,
+        children: cols.map((col) => ({
+          key: col.id,
+          title: createHighlightedNode(col.label, search),
+        })),
+      };
+    });
+  }, [filteredGroupedColumns, search]);
+
+  // Get all selected column IDs - memoized
+  const selectedColumnIds = useMemo(() => selectedColumns.map((col) => col.id), [selectedColumns]);
+
+  // Memoize the check handler to prevent re-creation
+  const handleCheck = useCallback(
+    (_: any, { node: { key, checked } }: { node: { key: string; checked: boolean } }) => {
+      // Check if this is a group node
+      if (key.startsWith('GROUP-')) {
+        const groupName = key.replace('GROUP-', '');
+        const groupColumns = filteredGroupedColumns[groupName] || [];
+
+        if (!checked) {
+          // Select all columns in this group
+          const columnsToAdd = groupColumns.filter((col) => !selectedColumns.some((c) => c.id === col.id));
+          setSelectedColumns([...selectedColumns, ...columnsToAdd]);
+        } else {
+          // Deselect all columns in this group
+          const columnIdsToRemove = groupColumns.map((col) => col.id);
+          setSelectedColumns(selectedColumns.filter((col) => !columnIdsToRemove.includes(col.id)));
+        }
+      } else {
+        // Single column toggle
+        const column = columns.find((col) => col.id === key);
+        if (column) {
+          toggleColumns([column]);
         }
-      });
-      setSelectedColumns(newSelection);
-    }
-  };
+      }
+    },
+    [filteredGroupedColumns, selectedColumns, setSelectedColumns, columns, toggleColumns],
+  );

-  return (
-    <DialogCombobox
-      componentId="mlflow.evaluations_overview_grouped.column_selector_dropdown"
-      label="Columns"
-      multiSelect
-    >
-      <DialogComboboxCustomButtonTriggerWrapper>
-        <Button
-          endIcon={<ChevronDownIcon />}
-          data-testid="column-selector-button"
-          componentId="mlflow.evaluations_review.table_ui.filter_button"
-        >
-          <div
-            css={{
-              display: 'flex',
-              gap: theme.spacing.sm,
-              alignItems: 'center',
-            }}
-          >
-            <ColumnsIcon />
-            {intl.formatMessage({
-              defaultMessage: 'Columns',
-              description: 'Evaluation review > evaluations list > filter dropdown button',
-n            })}
-          </div>
-        </Button>
-      </DialogComboboxCustomButtonTriggerWrapper>
-      <DialogComboboxContent
-        maxHeight={OPTION_HEIGHT * 15.5}
-        minWidth={300}
-        maxWidth={500}
-        loading={isMetadataLoading && !metadataError}
+  // Get all group keys for default expansion - memoized
+  const defaultExpandedKeys = useMemo(() => {
+    return Object.keys(sortedGroupedColumns).map((group) => getGroupKey(group));
+  }, [sortedGroupedColumns]);
+
+  const dropdownContent = useMemo(
+    () => (
+      <div
+        css={{
+          backgroundColor: theme.colors.backgroundPrimary,
+          width: 400,
+          border: `1px solid`,
+          borderColor: theme.colors.border,
+        }}
+        onKeyDown={(e) => {
+          if (e.key === 'Escape') {
+            setDropdownVisible(false);
+          }
+        }}
       >
         {metadataError ? (
           <div
@@ -161,42 +196,90 @@ export const EvaluationsOverviewColumnSelectorGrouped: React.FC<React.PropsWithC
             />
           </div>
         ) : (
-          <DialogComboboxOptionList>
-            <DialogComboboxOptionListSearch controlledValue={search} setControlledValue={setSearch}>
-              {Object.entries(filteredGroupedColumns).map(([groupName, cols]) => (
-                <React.Fragment key={groupName}>
-                  <DialogComboboxSectionHeader>{getGroupLabel(groupName)}</DialogComboboxSectionHeader>
-
-                  <DialogComboboxOptionListCheckboxItem
-                    value={`all-${groupName}`}
-                    checked={cols.every((col) => selectedColumns.some((c) => c.id === col.id))}
-                    onChange={() => handleSelectAllInGroup(cols)}
-                  >
-                    {intl.formatMessage(
-                      {
-                        defaultMessage: 'All {groupLabel}',
-                        description: 'Evaluation review > evaluations list > select all columns in group',
-                      },
-                      { groupLabel: getGroupLabel(groupName) },
-                    )}
-                  </DialogComboboxOptionListCheckboxItem>
-
-                  {cols.map((col) => (
-                    <DialogComboboxOptionListCheckboxItem
-                      key={col.id}
-                      value={col.label}
-                      checked={selectedColumns.some((c) => c.id === col.id)}
-                      onChange={() => handleToggle(col)}
-                    >
-                      {col.label}
-                    </DialogComboboxOptionListCheckboxItem>
-                  ))}
-                </React.Fragment>
-              ))}
-            </DialogComboboxOptionListSearch>
-          </DialogComboboxOptionList>
+          <>
+            <div css={{ padding: theme.spacing.md }}>
+              <Input
+                componentId="mlflow.traces.column_selector.search"
+                value={search}
+                prefix={<SearchIcon />}
+                placeholder={intl.formatMessage({
+                  defaultMessage: 'Search columns',
+                  description: 'Placeholder for column selector search input',
+                })}
+                allowClear
+                onChange={(e) => setSearch(e.target.value)}
+              />
+            </div>
+            <div
+              css={{
+                maxHeight: 15 * 32,
+                overflowY: 'scroll',
+                overflowX: 'hidden',
+                paddingBottom: theme.spacing.md,
+                'span[title]': {
+                  whiteSpace: 'nowrap',
+                  textOverflow: 'ellipsis',
+                  overflow: 'hidden',
+                },
+              }}
+            >
+              <Tree
+                data-testid="column-selector-tree"
+                mode="checkable"
+                dangerouslySetAntdProps={{
+                  checkedKeys: selectedColumnIds,
+                  onCheck: handleCheck,
+                  // Disable animation for smoother performance
+                  motion: null,
+                }}
+                defaultExpandedKeys={defaultExpandedKeys}
+                treeData={treeData}
+              />
+            </div>
+          </>
         )}
-      </DialogComboboxContent>
-    </DialogCombobox>
+      </div>
+    ),
+    [
+      theme,
+      metadataError,
+      search,
+      intl,
+      selectedColumnIds,
+      handleCheck,
+      defaultExpandedKeys,
+      treeData,
+    ],
+  );
+
+  return (
+    <Dropdown
+      overlay={dropdownContent}
+      placement="bottomLeft"
+      trigger={['click']}
+      visible={isMetadataLoading ? false : dropdownVisible}
+      onVisibleChange={setDropdownVisible}
+    >
+      <Button
+        endIcon={<ChevronDownIcon />}
+        data-testid="column-selector-button"
+        componentId="mlflow.evaluations_review.table_ui.filter_button"
+        loading={isMetadataLoading && !metadataError}
+      >
+        <div
+          css={{
+            display: 'flex',
+            gap: theme.spacing.sm,
+            alignItems: 'center',
+          }}
+        >
+          <ColumnsIcon />
+          {intl.formatMessage({
+            defaultMessage: 'Columns',
+            description: 'Evaluation review > evaluations list > filter dropdown button',
+          })}
+        </div>
+      </Button>
+    </Dropdown>
   );
 };
PATCH

echo "Patch applied successfully."
