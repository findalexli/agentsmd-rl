# Table `column` Prop for Shared Column Defaults

## Problem

When using the Table component, developers often need to apply the same styling properties (such as `align: 'center'` or `ellipsis: true`) to many columns for visual consistency. Currently, each column must specify these properties individually, which is repetitive and error-prone. Adding a way to define default column properties at the table level would reduce duplication while still allowing individual columns to override when needed.

## Goal

Add a mechanism to the Table component that allows setting default column properties which apply to all columns unless explicitly overridden on individual columns.

## Requirements

1. **API Design**: Add a `column` prop to the Table component that accepts default column properties.

2. **Inheritance Behavior**: 
   - When a column doesn't explicitly define a property (like `align`), it should inherit from the table's `column` defaults
   - When a column explicitly defines a property, its value should override the default
   - Special columns (like row selection and expand columns) should be preserved unchanged

3. **Nested Groups**: The solution should handle nested column groups (columns with `children`) recursively.

4. **Property Filtering**: The `children` property from defaults should not be merged onto individual columns to avoid duplication issues.

5. **Type Safety**: TypeScript types should properly reflect the new prop.

6. **Testing**: Add tests that verify:
   - Default alignment is inherited by columns without explicit alignment
   - Per-column overrides take precedence over defaults
   - Special columns work correctly alongside regular columns with defaults

7. **Demo**: Create a demo file showing the feature with at least 3 columns, demonstrating both inherited defaults and per-column overrides.

8. **Integration Requirements**:
   - The `column` prop must not be passed through to the underlying rc-table component (it should be handled by Ant Design's Table before passing props downstream)
   - The solution should use utilities available in the `@rc-component/util` package for prop merging

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

## Reference

The PR diff shows the expected changes to `InternalTable.tsx`, the addition of a new hook file at `components/table/hooks/useFilledColumns.ts`, and updates to the test file and demo files.
