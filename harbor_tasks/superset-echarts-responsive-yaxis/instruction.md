# Adapt the ECharts timeseries y-axis to chart height

## Project

You are working in `/workspace/superset` — the Apache Superset repository checked out
at a specific commit. The relevant code lives under
`superset-frontend/plugins/plugin-chart-echarts/`.

## The problem

When the ECharts **timeseries** chart is rendered at small heights — e.g. inside a dense
dashboard cell — the y-axis labels, tick marks, split lines, and the legend all compete
for the limited vertical space, overlap each other, and clip against the cell border.
The chart is unreadable.

The chart's `transformProps` function in
`superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts`
currently produces the same y-axis configuration (axis lines, tick marks, split lines,
minor ticks, axis title, legend) and the same grid padding regardless of how short the
chart is. It also passes a fixed/default tick count to ECharts even on very tall charts
where that produces too few labels.

## Required behavior

Make the timeseries chart's y-axis **responsive to the rendered chart height** by
introducing three tiers, gated by two height thresholds (in pixels). The tier
determines what ECharts options the y-axis, axis ticks, split lines, legend, and grid
padding receive.

1. **Full charts — height ≥ 100px** ("compact" threshold): standard, uncompressed axis.
   The number of y-axis ticks should scale **proportionally with chart height**:
   one tick per `80` px of chart height, with a floor of `3` ticks.
   (Concretely: `splitNumber = max(3, floor(height / 80))`.)

2. **Compact charts — 60px ≤ height < 100px**: only the y-axis min/max boundary labels
   are shown. The axis line/ticks, split lines, minor ticks, minor split lines, axis
   title (`name`), and the legend are all suppressed at this tier — even if the user
   enabled `showLegend` in the form data, the legend must not render. The y-axis
   `splitNumber` must be `1` so ECharts renders only the boundary labels. Grid
   padding should be tightened (small top padding, and tightened bottom padding
   **only when the chart is not zoomable** — zoomable charts must preserve bottom
   space for the `dataZoom` slider).

3. **Micro charts — height < 60px** ("micro" threshold): all axis decorations are
   hidden — the axis label, min label, and max label are all suppressed so the
   chart renders as a sparkline-style line only.

In addition: for charts with axis labels visible, ECharts' `hideOverlap` option on
the y-axis label must be enabled so any remaining labels that would still collide
get suppressed by ECharts itself.

The two height thresholds (`100` and `60`) and the `pixels-per-tick` value (`80`)
must be added to the shared constants object
`TIMESERIES_CONSTANTS` in
`superset-frontend/plugins/plugin-chart-echarts/src/constants.ts` (alongside the
other layout constants there) and **referenced from `transformProps.ts` by name** —
do not hardcode the literal numbers in `transformProps.ts`. The constants must be
named `compactChartHeight`, `microChartHeight`, and `yAxisPixelsPerTick`.

## What stays unchanged

- All existing behavior for charts at heights ≥ 100px (full tier) must be preserved
  for users who haven't reduced their chart size, except that the y-axis tick count
  now scales with height (`max(3, floor(height/80))`) instead of using ECharts'
  default.
- The form data field `showLegend` still controls legend visibility on full-tier
  charts. It is only **overridden to hidden** when the chart drops into the compact
  or micro tier.
- The existing transformProps jest test file must continue to pass.

## Where to look

- `superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts`
  — the function that builds the `echartOptions` object (yAxis, legend, grid).
  The y-axis config is assembled into a `yAxis` variable; the legend config is
  passed via `getLegendProps(...)`; the grid padding is in `padding` from
  `getPadding(...)`.
- `superset-frontend/plugins/plugin-chart-echarts/src/constants.ts` — exports
  `TIMESERIES_CONSTANTS`, where the new height thresholds belong.
- `superset-frontend/plugins/plugin-chart-echarts/test/Timeseries/transformProps.test.ts`
  — existing jest tests for this transform; they must keep passing. Use the
  helper `createTestChartProps({ height, formData })` already defined there if you
  add new test cases.

## Running tests

```bash
cd /workspace/superset/superset-frontend
npx jest plugins/plugin-chart-echarts/test/Timeseries/transformProps.test.ts
```

Tests are run with `jest`. The grader runs an additional behavioral test file that
asserts each tier's expected output of `transformProps`. Among other things it
verifies:

- `legend.show === true` on a 400px chart with `showLegend: true`
- `legend.show === false` on an 80px chart with `showLegend: true`
- `yAxis.axisLabel.show === true` on an 80px chart
- `yAxis.axisLabel.show === false` on a 40px chart
- `yAxis.splitNumber === 1` on charts with height in `[60, 100)`
- A 500px chart's `yAxis.splitNumber` is greater than a 200px chart's
- At exactly 100px: full axis (`axisLabel.show === true`, `splitNumber >= 3`)
- At exactly 60px: compact axis (`axisLabel.show === true`, `splitNumber === 1`)
- At 59px: micro (`axisLabel.show === false`)
- Zoomable 80px chart: `grid.bottom > 5`

## Code Style Requirements

- Code is TypeScript — keep new code in `.ts` files and avoid introducing `any`
  types in production source.
- Avoid time-specific words ("now", "currently", "today") in code comments —
  comments should remain accurate when read in the future.
- New tests must use `test(...)` (not `describe(...)` nesting) and Jest +
  React Testing Library style only (no Enzyme).
