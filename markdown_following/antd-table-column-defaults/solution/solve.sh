#!/bin/bash
set -e

cd /workspace/ant-design

# Apply the gold patch for the 'column' feature
cat <<'PATCH' | git apply -
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
diff --git a/components/table/__tests__/Table.test.tsx b/components/table/__tests__/Table.test.tsx
index c99733ca9560..34b671c635d3 100644
--- a/components/table/__tests__/Table.test.tsx
+++ b/components/table/__tests__/Table.test.tsx
@@ -233,6 +233,43 @@ describe('Table', () => {
       });
   });

+  it('supports column align with per-column override and special columns', () => {
+    const { container } = render(
+      <Table
+        columns={[
+          { title: 'Name', dataIndex: 'name' },
+          Table.EXPAND_COLUMN,
+          {
+            title: 'Info',
+            children: [{ title: 'Age', dataIndex: 'age', align: 'right' }],
+          },
+          Table.SELECTION_COLUMN,
+        ]}
+        dataSource={[
+          {
+            key: '1',
+            name: 'Jack',
+            age: 20,
+          },
+        ]}
+        column={{ align: 'center' }}
+        expandable={{ expandedRowRender: () => null }}
+        rowSelection={{}}
+        pagination={false}
+      />,
+    );
+
+    const cells = container.querySelectorAll('tbody tr')[0].querySelectorAll('td');
+
+    expect(cells).toHaveLength(4);
+    expect(cells[0]).toHaveStyle({ textAlign: 'center' });
+    expect(cells[0].textContent).toEqual('Jack');
+    expect(cells[1].querySelector('.ant-table-row-expand-icon')).toBeTruthy();
+    expect(cells[2]).toHaveStyle({ textAlign: 'right' });
+    expect(cells[2].textContent).toEqual('20');
+    expect(cells[3].querySelector('.ant-checkbox-input')).toBeTruthy();
+  });
+
   it('warn about rowKey when using index parameter', () => {
     warnSpy.mockReset();
     const columns: TableProps<any>['columns'] = [
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

# Also create the demo file and its documentation
cat <<'DEMO_TSX' > components/table/demo/column-defaults.tsx
import React from 'react';
import type { TableProps } from 'antd';
import { Table } from 'antd';

interface DataType {
  key: React.Key;
  name: string;
  address: string;
  description: string;
}

const columns: TableProps<DataType>['columns'] = [
  {
    title: 'Name',
    dataIndex: 'name',
    width: 140,
  },
  {
    title: 'Description',
    dataIndex: 'description',
    width: 180,
  },
  {
    title: 'Address',
    dataIndex: 'address',
    align: 'left',
    width: 220,
  },
];

const data: DataType[] = [
  {
    key: '1',
    name: 'John Brown',
    description: 'Shared column props let repeated column settings live on the table.',
    address: 'No. 1 Lake Park Road, Hangzhou, Zhejiang, China',
  },
  {
    key: '2',
    name: 'Jim Green',
    description: 'Columns can still override the default alignment or other shared props.',
    address: 'No. 99 Garden Avenue, Pudong, Shanghai, China',
  },
];

const App: React.FC = () => (
  <Table<DataType>
    columns={columns}
    dataSource={data}
    column={{ align: 'center', ellipsis: true }}
    pagination={false}
  />
);

export default App;
DEMO_TSX

cat <<'DEMO_MD' > components/table/demo/column-defaults.md
## zh-CN

通过 `column` 在 Table 上统一设置列属性，并按需在单列上覆盖。

## en-US

Use `column` to set shared column props on the table and override them per column when needed.
DEMO_MD

echo "Patch applied successfully"
