# Fix Stacked Horizontal Bar Chart Axis Bounds

## Problem

Horizontal stacked bar charts in the ECharts plugin are displaying incorrectly when the "Truncate Y Axis" option is enabled. The bars appear clipped and the x-axis shows duplicate labels.

**Symptoms:**
1. Stacked bars don't reach their full combined height - they appear cut off at roughly half their expected height
2. The x-axis shows duplicate numeric labels (e.g., "1 2 2 3 3 4 4" instead of "1 2 3 4")

## Relevant Code

The issue is in the ECharts timeseries transform logic:

- **File**: `superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts`
- **Function**: `transformProps()`
- **Area**: The `shouldCalculateDataBounds` block (around line 682) that handles horizontal bar chart axis bounds

When `shouldCalculateDataBounds` is true (which happens for horizontal bar charts with truncated Y axis), the code calculates `yAxisMax` using `dataMax` - the maximum value across all individual series.

However, for **stacked** horizontal bar charts, this is incorrect. The axis maximum must accommodate the **stacked total** per row, not the maximum of any single series.

## Example

Consider a dataset with three metrics (High, Low, Medium) and one row:
- Team A: High=2, Low=2, Medium=4

For a stacked horizontal bar:
- Individual series max = 4 (Medium)
- Stacked total for Team A = 2 + 2 + 4 = 8

The x-axis max should be 8 to show the full stacked bar, not 4.

## Related Areas

Also check the `stackDimension` series assignment logic (around line 659) where series are grouped for stacking. There may be an issue with how dimension values are assigned to the `stack` property.

## Testing Context

The test framework will evaluate your fix by:
1. Creating a horizontal stacked bar chart with multiple metrics
2. Verifying that `xAxis.max` is set to at least the stacked total (not the individual series max)
3. Ensuring non-stacked horizontal bar charts still work correctly with individual series max
4. Checking that the code compiles without TypeScript errors

Run tests from the plugin directory: `superset-frontend/plugins/plugin-chart-echarts`
