# Fix Gantt view "Error invalid date" on running DagRun

The Gantt chart in the Airflow UI is displaying "Error invalid date" when viewing running DagRuns. This is a date parsing issue in the chart's x-axis scale calculations.

## Bug Description

When the Gantt chart renders tasks, it calculates scale min/max values for the time axis. The current implementation uses `new Date().getTime()` to parse date strings, which fails for non-UTC timezone abbreviations and returns `NaN`. This causes Chart.js's time scale to crash with an "invalid date" error.

## Affected Code

The bug is in `airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts` in the `createChartOptions` function. Look for the x-axis scale min/max calculations.

## Symptoms

1. Opening the Gantt view for a running DagRun shows "Error invalid date"
2. The chart fails to render when any task has a null end date (still running)
3. Browser console shows Chart.js errors related to invalid time values

## Expected Behavior

The Gantt chart should:
1. Parse ISO date strings reliably regardless of timezone format
2. Handle null dates gracefully (for running tasks)
3. Calculate proper min/max scale values without returning NaN

## Context

The fix involves replacing `new Date(item.x[...]).getTime()` with `dayjs(item.x[...]).valueOf()` which handles date parsing more reliably, especially for edge cases like null values and timezone abbreviations.

The project uses:
- dayjs for date manipulation (already imported in the file)
- Vitest for testing
- ESLint for linting
- TypeScript for type checking

## Files to Modify

- `airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts` - Fix the date parsing

The fix should be applied to both the `min` and `max` scale calculations in the `createChartOptions` function.
