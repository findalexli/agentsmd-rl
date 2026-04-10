# Remove react-icons Dependency from Table Plugins

## Problem

The `plugin-chart-table` and `plugin-chart-pivot-table` plugins currently depend on the `react-icons` package (83MB) just for 3 sort indicator icons. Since the project already uses Ant Design components throughout, these icons should be replaced with equivalent icons from `@ant-design/icons`, allowing the removal of the unnecessary dependency.

## Files to Modify

You need to modify files in two plugin directories:

1. **`plugins/plugin-chart-table/`** - The main table chart component
   - `src/TableChart.tsx` - Contains the `SortIcon` component that renders sort indicators
   - `package.json` - Has the `react-icons` dependency that should be removed

2. **`plugins/plugin-chart-pivot-table/`** - The pivot table chart component
   - `src/react-pivottable/TableRenderers.tsx` - Contains sort indicator logic for pivot tables
   - `package.json` - Has the `react-icons` dependency that should be removed

## Current Icon Usage

Both files currently import sort icons from `react-icons/fa`:
- `FaSort` - for unsorted/neutral state
- `FaSortUp` - for ascending sort
- `FaSortDown` - for descending sort

These should be replaced with equivalent Ant Design icons from `@ant-design/icons`:
- `ColumnHeightOutlined` - for unsorted/neutral state (double-ended arrow)
- `CaretUpOutlined` - for ascending sort
- `CaretDownOutlined` - for descending sort

## Requirements

1. Remove `react-icons` from both package.json `dependencies`
2. Replace all react-icons imports with imports from `@ant-design/icons`
3. Update the icon component usage to use the new antd icon components
4. Ensure TypeScript compilation passes
5. Ensure the code follows the project's linting rules
6. Keep the same functionality - only the icon components should change

## Notes

- Look at the `SortIcon` component in `TableChart.tsx` - it's a simple functional component
- In the pivot table's `TableRenderers.tsx`, the sort icon selection is done via a dynamic component assignment
- The project already uses `@ant-design/icons` elsewhere, so it will already be available as a transitive dependency
- Follow the existing code style in each file for imports and JSX syntax
