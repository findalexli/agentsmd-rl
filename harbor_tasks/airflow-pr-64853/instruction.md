# Fix Gantt View "Error invalid date" Bug

The Gantt chart in the Airflow UI crashes with "Error invalid date" when viewing a running DagRun. The error appears when the chart tries to calculate the x-axis scale boundaries.

## Symptoms

- Opening the Gantt view for an active (running) DagRun shows an error
- The Chart.js time scale fails to render
- The error message mentions "invalid date"
- The scale min/max values become `NaN` instead of valid timestamps

## Where to Look

The Gantt chart utilities are in:
- `airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts`

The `createChartOptions` function calculates the x-axis scale `min` and `max` values by parsing date strings from the Gantt data items.

## Technical Context

The Gantt data items contain date strings in ISO format (e.g., `"2024-03-14T10:00:00+00:00"`). These date strings need to be converted to timestamps (milliseconds since epoch) for the Chart.js time scale configuration.

The date parsing happens for two fields:
- `item.x[0]` - the start date field
- `item.x[1]` - the end date field

Both the `min` and `max` scale calculations use these values.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
