# Replace react-icons with antd icons in table chart plugins

The `react-icons` package is a heavy dependency (83MB) that is only used for three sort indicator icons in the table chart plugins. The project already uses `@ant-design/icons` extensively, which provides equivalent icons.

## Problem

Two table chart plugins depend on `react-icons` for sort column indicators:

1. `superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx`
2. `superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx`

These files import `FaSort`, `FaSortUp`, and `FaSortDown` from `react-icons/fa` to show:
- A neutral/unsorted indicator (double-ended arrow)
- An ascending sort indicator (up arrow)
- A descending sort indicator (down arrow)

## Task

Replace the `react-icons` imports and usage with icons from `@ant-design/icons`. The sort icon mapping must be:

- `FaSort` (neutral/unsorted) → `ColumnHeightOutlined`
- `FaSortUp` (ascending) → `CaretUpOutlined`
- `FaSortDown` (descending) → `CaretDownOutlined`

Import all three icons (`CaretUpOutlined`, `CaretDownOutlined`, `ColumnHeightOutlined`) from `@ant-design/icons`.

The sort state logic must remain correct:
- In `TableChart.tsx`, the `SortIcon` component uses `isSortedDesc` to choose between ascending and descending icons
- In `TableRenderers.tsx`, the icon selection uses `sortingOrder[key] === 'asc'` to determine direction

Also update the package.json files in both plugin directories to remove the `react-icons` dependency.

## Files to modify

- `superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx`
- `superset-frontend/plugins/plugin-chart-table/package.json`
- `superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx`
- `superset-frontend/plugins/plugin-chart-pivot-table/package.json`