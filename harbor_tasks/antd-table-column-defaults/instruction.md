# Task: Add Table `column` Prop for Shared Column Defaults

## Problem

The Table component currently requires developers to repeat the same column properties (like `align: 'center'` or `ellipsis: true`) on every column when they want consistent styling across multiple columns. This is tedious and error-prone.

## Goal

Add a `column` prop to the Table component that allows setting default column properties that apply to all columns unless explicitly overridden.

## Requirements

1. **Add the `column` prop to TableProps interface**: Add a new optional `column` property typed as `Partial<ColumnType<RecordType>>` to the TableProps interface in `InternalTable.tsx`.

2. **Create a `useFilledColumns` hook**: Create a new hook at `components/table/hooks/useFilledColumns.ts` that:
   - Takes `columns` and `column` (defaults object) as parameters
   - Returns columns with defaults applied when `column` is provided
   - Uses `mergeProps` from `@rc-component/util` to merge (column defaults come first, individual column props override)
   - Returns original columns unchanged when `column` is not provided
   - Preserves `SELECTION_COLUMN` and `EXPAND_COLUMN` unchanged (check with `===`)
   - Recursively handles nested column groups (columns with `children` arrays)
   - Omits `children` from the defaults when merging to avoid structure issues

3. **Integrate in InternalTable**:
   - Import the `useFilledColumns` hook
   - Destructure the `column` prop from component props
   - Rename the existing `baseColumns` memo to `rawColumns` and create a new `baseColumns` using `useFilledColumns(rawColumns, column)`
   - Add `'column'` to the `omit()` call that creates `tableProps` to avoid passing it to rc-table

4. **Add tests**: Add a test in `components/table/__tests__/Table.test.tsx` that verifies:
   - Default alignment from `column` is applied to columns without explicit alignment
   - Per-column override takes precedence over defaults
   - Special columns (EXPAND_COLUMN, SELECTION_COLUMN) work correctly alongside regular columns

5. **Add demo**: Create a demo at `components/table/demo/column-defaults.tsx` showing the feature with at least 3 columns where:
   - Some inherit defaults (e.g., `align: 'center'`)
   - At least one overrides (e.g., `align: 'left'`)

## Important Notes

- **Demo imports**: Use absolute imports (`from 'antd'`, `from 'antd/es/table'`) in demo files, never relative imports (`../`, `./`)
- **Test imports**: Use relative imports (`from '..'`, `from '../index'`) in test files, never absolute imports (`from 'antd'`)
- Use the existing utilities: `mergeProps` and `omit` from `@rc-component/util`
- The constants `SELECTION_COLUMN` and `EXPAND_COLUMN` are available from `../hooks/useSelection` and `@rc-component/table`
- Refer to the PR description in the task files for more implementation details if needed

## Files to Modify

- `components/table/InternalTable.tsx` - Add prop type, destructuring, hook usage
- `components/table/hooks/useFilledColumns.ts` - Create new file (main implementation)
- `components/table/__tests__/Table.test.tsx` - Add tests
- `components/table/demo/column-defaults.tsx` - Create demo
- `components/table/demo/column-defaults.md` - Create demo description

## Verification

After implementation, the following should work:
- TypeScript compilation passes
- A Table with `column={{ align: 'center' }}` should center-align all columns without explicit alignment
- Columns with explicit `align: 'right'` should right-align despite the default
