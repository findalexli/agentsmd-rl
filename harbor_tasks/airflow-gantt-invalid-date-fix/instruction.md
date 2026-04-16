# Fix Gantt View "Error invalid date" on Running DagRun

## Problem

The Gantt chart in the Airflow UI displays an "Error invalid date" error when viewing a running DagRun. The issue occurs in the chart's x-axis scale computation, where ISO date strings are converted to millisecond timestamps. For running tasks, the current conversion logic can produce `NaN` values, which causes the chart to fail rendering.

## Expected Behavior

The x-axis scale computation must produce valid millisecond timestamps for all chart data points, including running tasks whose end dates are represented as ISO date strings. Any date-to-timestamp conversion in the scale computation should yield a valid number, never `NaN`.

## Verification

After applying the fix, the following conditions must be satisfied:

1. The Gantt chart utility source code must contain `dayjs(item.x[1]).valueOf()` and `dayjs(item.x[0]).valueOf()` in its scale calculation logic
2. The patterns `new Date(item.x[1] ?? "").getTime()` and `new Date(item.x[0] ?? "").getTime()` must not appear anywhere in the scale calculation

Additionally, run the following commands from the UI source directory (`airflow-core/src/airflow/ui`):

1. TypeScript should compile without errors:
   ```
   npx tsc --noEmit -p tsconfig.app.json
   ```
2. Lint should pass:
   ```
   pnpm run lint
   ```
3. Format check should pass:
   ```
   npx prettier --check src/layouts/Details/Gantt/utils.ts
   ```
4. Build should pass:
   ```
   pnpm run build
   ```
5. Unit tests should pass:
   ```
   pnpm test
   ```
