# DagVersionSelect Shows All Versions Regardless of Selected DagRun

## Problem

The `DagVersionSelect` component in the Airflow UI (`airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx`) displays all available DAG versions in its dropdown, even when a specific DagRun is selected.

## Expected Behavior

When a user navigates to a specific DagRun, the version dropdown should only show the DAG versions that are associated with that particular run. When no DagRun is selected, all versions should be shown as they are today.

The component should determine which DagRun (if any) is currently selected based on the URL/route parameters, fetch the corresponding DagRun data from the API, and use the version information from that response to filter the dropdown options.

## Current Behavior

The dropdown always shows all available versions regardless of whether a DagRun is selected or not. This makes it confusing for users who expect to see only the relevant versions for their selected run.

## Relevant Files

- `airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx` - The component that needs to be fixed
