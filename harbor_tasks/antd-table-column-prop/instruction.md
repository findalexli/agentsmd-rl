# Task: Add `column` Property to Table Component

## Problem Statement

The Table component currently requires developers to set common column properties (like `align: 'center'`, `ellipsis: true`) on each individual column. This leads to repetitive code when multiple columns share the same settings.

You need to add a `column` property to the Table component that allows setting **default column props** that apply to all columns. Individual columns should still be able to override these defaults.

## Requirements

### Functional Requirements

1. **Add `column` property to Table**: The property should accept `Partial<ColumnType<RecordType>>` and provide default values for columns

2. **Merge behavior**: When the `column` property is provided:
   - Columns inherit properties from `column` when they don't explicitly define that property
   - Explicit column properties take precedence over defaults
   - Column groups (with `children`) should also be merged correctly

3. **Special columns must be preserved**: The internal `SELECTION_COLUMN` and `EXPAND_COLUMN` markers should be returned unchanged

4. **Don't pass to rc-table**: The `column` prop should be omitted from props passed to the underlying rc-table component

### Files to Modify

1. **`components/table/hooks/useFilledColumns.ts`** (NEW FILE)
   - Create a custom hook that takes `columns` and an optional `column` defaults object
   - Returns columns with defaults merged in
   - Uses `mergeProps` from `@rc-component/util` for merging
   - Handles recursive merging for column groups
   - Preserves `SELECTION_COLUMN` and `EXPAND_COLUMN` markers

2. **`components/table/InternalTable.tsx`**
   - Add `column` property to `TableProps` interface
   - Destructure `column` from props
   - Rename the existing `baseColumns` memo to `rawColumns`
   - Call `useFilledColumns(rawColumns, column)` to get the actual `baseColumns`
   - Add `'column'` to the `omit()` call for `tableProps`

### Key Implementation Details

- Use `React.useMemo` to avoid recreating columns on every render
- Use `omit(column, ['children'])` when merging to avoid type issues with column groups
- The hook should early-return columns unchanged if `column` is not provided

### Example Usage

```tsx
<Table
  columns={[
    { title: 'Name', dataIndex: 'name' },
    { title: 'Age', dataIndex: 'age', align: 'right' }, // overrides default
  ]}
  dataSource={data}
  column={{ align: 'center', ellipsis: true }} // defaults for all columns
/>
```

In this example:
- The "Name" column would have `align: 'center'` and `ellipsis: true`
- The "Age" column would have `align: 'right'` (explicit override) and `ellipsis: true`

## Success Criteria

- TypeScript compiles without errors
- The new hook correctly merges column defaults
- Special columns (SELECTION_COLUMN, EXPAND_COLUMN) are preserved
- Column groups with children are handled recursively
- The `column` prop doesn't leak to rc-table
