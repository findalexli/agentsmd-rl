# Remove react-icons Dependency from Table Plugins

## Problem

The `plugin-chart-table` and `plugin-chart-pivot-table` plugins currently include `react-icons` as a direct dependency. This package is large (83MB) and is used only for 3 sort indicator icons. The project already uses Ant Design throughout and `@ant-design/icons` is available as a transitive dependency.

**Goal**: Remove the `react-icons` dependency and replace the sort indicator icons with equivalent icons from `@ant-design/icons`.

## What to Change

Both plugins have sort indicator icons that are currently rendered using `react-icons/fa` imports. These imports and the associated dependency must be removed.

### Files to Update

For each plugin, you need to update:
1. The `package.json` `dependencies` section — remove the `react-icons` entry
2. The source file(s) that import from `react-icons/fa` — update imports and icon usage

### What the Tests Check

The tests verify the following for each plugin:

**Table plugin (`plugins/plugin-chart-table/`)**:
- `package.json` has no `react-icons` in `dependencies`
- `src/TableChart.tsx` does not import from `react-icons/fa` or reference `FaSort`
- `src/TableChart.tsx` imports `CaretUpOutlined`, `CaretDownOutlined`, and `ColumnHeightOutlined` from `@ant-design/icons`
- `src/TableChart.tsx` contains JSX for the three antd icon components

**Pivot table plugin (`plugins/plugin-chart-pivot-table/`)**:
- `package.json` has no `react-icons` in `dependencies`
- `src/react-pivottable/TableRenderers.tsx` does not import from `react-icons/fa` or reference `FaSort`
- `src/react-pivottable/TableRenderers.tsx` imports `CaretUpOutlined`, `CaretDownOutlined`, and `ColumnHeightOutlined` from `@ant-design/icons`
- `src/react-pivottable/TableRenderers.tsx` uses these icons appropriately for sort indicators

## Verification

After making changes:
1. `npm run plugins:build` should pass (TypeScript compilation)
2. `npm test -- --testPathPatterns=plugin-chart-table --maxWorkers=1` should pass
3. `npm test -- --testPathPatterns=plugin-chart-pivot-table --maxWorkers=1` should pass
