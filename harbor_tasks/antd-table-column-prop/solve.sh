#!/bin/bash
set -e

cd /workspace/ant-design

# Apply the gold patch for Table column feature
patch -p1 << 'PATCH'
diff --git a/components/table/InternalTable.tsx b/components/table/InternalTable.tsx
index acda8a64f748..2468f89a9078 100644
--- a/components/table/InternalTable.tsx
+++ b/components/table/InternalTable.tsx
@@ -31,6 +31,7 @@ import renderExpandIcon from './ExpandIcon';
 import useContainerWidth from './hooks/useContainerWidth';
 import type { FilterConfig, FilterState } from './hooks/useFilter';
 import useFilter, { getFilterData } from './hooks/useFilter';
+import useFilledColumns from './hooks/useFilledColumns';
 import useLazyKVMap from './hooks/useLazyKVMap';
 import usePagination, { DEFAULT_PAGE_SIZE, getPaginationParam } from './hooks/usePagination';
 import useSelection from './hooks/useSelection';
@@ -136,6 +137,7 @@ export interface TableProps<RecordType = AnyObject>
   styles?: TableSemanticAllType<RecordType>['stylesAndFn'];
   dropdownPrefixCls?: string;
   dataSource?: RcTableProps<RecordType>['data'];
+  column?: Partial<ColumnType<RecordType>>;
   columns?: ColumnsType<RecordType>;
   pagination?: false | TablePaginationConfig;
   loading?: boolean | SpinProps;
@@ -185,6 +187,7 @@ const InternalTable = <RecordType extends AnyObject = AnyObject>(
     rowSelection,
     rowKey: customizeRowKey,
     rowClassName,
+    column,
     columns,
     children,
     childrenColumnName: legacyChildrenColumnName,
@@ -205,10 +208,11 @@ const InternalTable = <RecordType extends AnyObject = AnyObject>(

   const warning = devUseWarning('Table');

-  const baseColumns = React.useMemo(
+  const rawColumns = React.useMemo(
     () => columns || (convertChildrenToColumns(children) as ColumnsType<RecordType>),
     [columns, children],
   );
+  const baseColumns = useFilledColumns(rawColumns, column);
   const needResponsive = React.useMemo(
     () => baseColumns.some((col: ColumnType<RecordType>) => col.responsive),
     [baseColumns],
@@ -222,7 +226,12 @@ const InternalTable = <RecordType extends AnyObject = AnyObject>(
     return baseColumns.filter((c) => !c.responsive || c.responsive.some((r) => matched.has(r)));
   }, [baseColumns, screens]);

-  const tableProps: TableProps<RecordType> = omit(props, ['className', 'style', 'columns']);
+  const tableProps: TableProps<RecordType> = omit(props, [
+    'className',
+    'style',
+    'column',
+    'columns',
+  ]);

   const { locale: contextLocale = defaultLocale, table } =
     React.useContext<ConfigConsumerProps>(ConfigContext);
diff --git a/components/table/hooks/useFilledColumns.ts b/components/table/hooks/useFilledColumns.ts
new file mode 100644
index 000000000000..5843327282fe
--- /dev/null
+++ b/components/table/hooks/useFilledColumns.ts
@@ -0,0 +1,49 @@
+import * as React from 'react';
+import { EXPAND_COLUMN } from '@rc-component/table';
+import { mergeProps, omit } from '@rc-component/util';
+
+import type { AnyObject } from '../../_util/type';
+import { SELECTION_COLUMN } from './useSelection';
+import type { ColumnGroupType, ColumnsType, ColumnType } from '../interface';
+
+const useFilledColumns = <RecordType extends AnyObject = AnyObject>(
+  columns: ColumnsType<RecordType>,
+  column?: Partial<ColumnType<RecordType>>,
+) =>
+  React.useMemo(() => {
+    if (!column) {
+      return columns;
+    }
+
+    const fillColumns = (currentColumns: ColumnsType<RecordType>): ColumnsType<RecordType> =>
+      currentColumns.map((col) => {
+        if (col === SELECTION_COLUMN || col === EXPAND_COLUMN) {
+          return col;
+        }
+
+        if ('children' in col && Array.isArray(col.children)) {
+          const mergedColumn = mergeProps(
+            column as Partial<ColumnGroupType<RecordType>>,
+            col as Partial<ColumnGroupType<RecordType>>,
+          ) as ColumnGroupType<RecordType>;
+
+          return {
+            ...mergedColumn,
+            children: fillColumns(col.children),
+          } as ColumnGroupType<RecordType>;
+        }
+
+        const columnWithoutChildren = omit(column as Partial<ColumnGroupType<RecordType>>, [
+          'children',
+        ]) as Partial<ColumnType<RecordType>>;
+
+        return mergeProps(
+          columnWithoutChildren,
+          col as Partial<ColumnType<RecordType>>,
+        ) as ColumnType<RecordType>;
+      });
+
+    return fillColumns(columns);
+  }, [columns, column]);
+
+export default useFilledColumns;
PATCH

# Install dependencies
npm install

echo "Gold patch applied successfully"
