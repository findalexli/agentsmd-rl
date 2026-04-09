# Fix DagVersionSelect to Filter Options Based on Selected DagRun

## Problem

The `DagVersionSelect` component in the Airflow UI shows all DAG versions in the dropdown, regardless of whether a specific DagRun is selected. This causes confusion because:

1. When viewing a specific DagRun in the Graph view, the version dropdown still shows ALL versions for the DAG
2. Users can select a version that doesn't match the selected run's structure
3. The UI becomes inconsistent - showing one run but allowing selection of unrelated versions

## Your Task

Modify the `DagVersionSelect` component to filter the available version options based on the selected DagRun.

## Key Details

- **File to modify**: `airflow-core/src/airflow/ui/src/components/DagVersionSelect.tsx`
- **Test file to create**: `airflow-core/src/airflow/ui/src/components/DagVersionSelect.test.tsx`

### Expected Behavior

1. When NO DagRun is selected (no `runId` in URL params): Show ALL versions for the DAG
2. When a DagRun IS selected (`runId` present in URL params): Show ONLY the versions used by that specific run

### Technical Context

- The component uses `useParams()` from react-router to get route parameters
- The component already uses `useDagVersionServiceGetDagVersions` to fetch all versions
- DagRun data is available via `useDagRunServiceGetDagRun` hook from `openapi/queries`
- A DagRun object has a `dag_versions` array containing versions associated with that run
- Versions should be sorted by `version_number` in descending order (newest first)
- The component uses Chakra UI's `Select` component with a `createListCollection` for options

### Testing Requirements

Add tests in a new test file that verify:
1. All versions are shown when no run is selected
2. Only the run's versions are shown when a run is selected

Use vitest and follow the existing mocking patterns in the codebase for:
- `react-router-dom` (especially `useParams`)
- `openapi/queries` hooks
- `src/hooks/useSelectedVersion`

### References

- Related issue: #51487 - DagVersionSelect shows unrelated versions when a DagRun is selected
- Look at how other components in the codebase mock React Router and API hooks for tests
