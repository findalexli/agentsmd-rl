# DagVersionSelect shows incorrect versions when viewing a specific DagRun

## Problem

In the Airflow UI's Graph view, when a user selects a specific DagRun to view, the version dropdown (`DagVersionSelect`) shows all versions for the DAG instead of only the versions that are relevant to the selected run.

This is confusing because users may select a version that doesn't match the selected run's structure, leading to unexpected behavior or display issues.

## Expected Behavior

- When a DagRun is selected (indicated by a `runId` parameter in the route), the version dropdown should show only the versions associated with that specific run.
- When no DagRun is selected, all versions should be shown as before.

## Technical Context

The component is at `airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx`.

- The route for a DagRun's graph view includes a `runId` parameter alongside `dagId`.
- The codebase provides API hooks in the `openapi/queries` module for fetching DagRun and DagVersion data. The DagRun response includes a `dag_versions` array field containing the versions associated with that run.
- The existing component already fetches all DAG versions. It needs to also be aware of the selected run and conditionally display only that run's versions when applicable.

## Constraints

- TypeScript must compile without errors.
- ESLint must pass.
- Prettier formatting must be correct.
- Existing component tests must continue to pass.
