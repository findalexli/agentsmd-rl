# Table `column` Prop for Shared Column Defaults

## Problem

The Table component requires developers to repeat the same column properties (like `align: 'center'` or `ellipsis: true`) on every column for consistent styling. This is tedious and error-prone.

## Goal

Add a `column` prop to the Table component that sets default column properties applying to all columns unless explicitly overridden.

## Functional Requirements

The implementation must satisfy the following behavioral specifications:

1. **Type definition**: The `TableProps` interface must include a `column` property typed as `Partial<ColumnType<RecordType>>`.

2. **Hook behavior**: A hook at `components/table/hooks/useFilledColumns.ts` must:
   - Accept `columns` and an optional `column` defaults object
   - Return columns with defaults applied when the `column` parameter is provided
   - Return the original columns array unchanged when `column` is not provided (check with `if (!column)`)
   - Use `mergeProps` from `@rc-component/util` for merging, with individual column props taking precedence over defaults
   - Preserve system columns (`SELECTION_COLUMN`, `EXPAND_COLUMN`) using `===` identity checks
   - Recursively handle nested column groups (columns with `children` arrays) via a `fillColumns` function
   - Omit the `children` property from the defaults object before merging

3. **Integration**: In `InternalTable.tsx`:
   - Import the hook as `import useFilledColumns from './hooks/useFilledColumns'`
   - Destructure the `column` prop from component props
   - Pass both the base columns and `column` defaults to the hook
   - Omit `'column'` from props passed to rc-table

4. **Tests**: Add tests verifying alignment inheritance, per-column override precedence, and correct handling of special columns alongside regular columns.

5. **Demo**: Create a demo file demonstrating the feature with at least 3 columns showing both inherited defaults and per-column overrides.

## Required String Patterns

The following exact strings must appear in the specified files for the implementation to pass validation:

**In `InternalTable.tsx`:**
- `column?: Partial<ColumnType<RecordType>>`
- `import useFilledColumns from './hooks/useFilledColumns'`
- `useFilledColumns(rawColumns, column)`
- `column,` (destructuring)
- `rawColumns`
- `'column',` (in omit call)

**In `useFilledColumns.ts`:**
- `mergeProps`
- `SELECTION_COLUMN`
- `EXPAND_COLUMN`
- `col === SELECTION_COLUMN || col === EXPAND_COLUMN`
- `fillColumns`
- `if (!column)`
- `return columns`
- `'children' in col`
- `Array.isArray(col.children)`
- `fillColumns(col.children)`
- `omit(column` and `'children'`

## Import Conventions

- **Demo files**: Use absolute imports (`from 'antd'`, `from 'antd/es/table'`), never relative imports
- **Test files**: Use relative imports (`from '..'`, `from '../index'`), never absolute imports from `'antd'`

## Verification

After implementation:
- TypeScript compilation passes
- `npx biome lint components/table/` passes
- `npx eslint components/table/InternalTable.tsx` passes
- `npm test -- components/table/__tests__/Table.test.tsx` passes
- A Table with `column={{ align: 'center' }}` centers all columns without explicit alignment
- Columns with explicit `align: 'right'` right-align despite the default