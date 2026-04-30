# Table `column` Prop for Shared Column Defaults

## Problem

When using the Table component, developers often need to apply the same styling properties (such as `align: 'center'` or `ellipsis: true`) to many columns for visual consistency. Currently, each column must specify these properties individually, which is repetitive and error-prone. Adding a way to define default column properties at the table level would reduce duplication while still allowing individual columns to override when needed.

## Goal

Add a mechanism to the Table component that allows setting default column properties which apply to all columns unless explicitly overridden on individual columns.

## Requirements

1. **API Design**: Add a `column` prop to the Table component that accepts default column properties (a `Partial<ColumnType>`).

2. **Inheritance Behavior**:
   - When a column doesn't explicitly define a property (like `align`), it should inherit from the table's `column` defaults.
   - When a column explicitly defines a property, its value should override the default.
   - Built-in special columns exposed on the Table (`Table.SELECTION_COLUMN` and `Table.EXPAND_COLUMN`) must be preserved unchanged — defaults must not be merged onto them.

3. **Nested Groups**: The solution should handle nested column groups (columns with `children`) recursively, applying defaults to the group itself and to its children.

4. **Property Filtering**: The `children` property from `column` defaults should never be merged onto individual columns (to avoid accidentally injecting child columns).

5. **Type Safety**: TypeScript types should properly reflect the new prop.

6. **Hook Surface**: Expose the merge logic as a reusable React hook named `useFilledColumns` placed under `components/table/hooks/`. The hook must accept `(columns, columnDefaults)` and return a `ColumnsType` array; when `columnDefaults` is falsy it must return the input array unchanged (referential identity preserved).

7. **Testing**: Add a test in the existing Table test file that renders a Table with `column={{ align: 'center' }}`, mixes regular columns, a nested group, `Table.EXPAND_COLUMN`, and `Table.SELECTION_COLUMN`, and verifies the resulting cell `textAlign` reflects the inheritance/override rules.

8. **Demo**: Create a new demo file `components/table/demo/column-defaults.tsx` (and accompanying `.md`) that demonstrates the feature with at least 3 columns, showing inherited defaults and at least one per-column override.

9. **Integration Requirements**:
   - The `column` prop must not be passed through to the underlying `rc-table` component — Ant Design's Table layer must consume and strip it before forwarding props.
   - Use the prop-merging utilities available in the `@rc-component/util` package.

## Import Conventions

- **Demo files**: Use absolute imports (`from 'antd'`, `from 'antd/es/table'`), never relative imports.
- **Test files**: Use relative imports (`from '..'`, `from '../index'`), never absolute imports from `'antd'`.

## Verification

After implementation:
- TypeScript compilation passes.
- `npx biome lint components/table/` passes.
- `npx eslint components/table/InternalTable.tsx` passes.
- `npm test -- components/table/__tests__/Table.test.tsx` passes.
- A Table rendered with `column={{ align: 'center' }}` centers all regular columns without explicit alignment.
- A column with explicit `align: 'right'` remains right-aligned despite the default.
- `Table.EXPAND_COLUMN` and `Table.SELECTION_COLUMN` render their built-in markers (expand icon / row-selection checkbox) and are not affected by the defaults.
