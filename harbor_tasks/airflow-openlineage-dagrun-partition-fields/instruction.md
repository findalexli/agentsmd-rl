# Task: Add Partition Fields to OpenLineage DagRun Events

## Problem

The OpenLineage integration in Airflow is not including partition information when serializing DagRun data for lineage events. Airflow 3.2 introduced `partition_key` and `partition_date` attributes on DagRun, but these fields are absent from the serialized output sent to lineage backends.

## Symptom

When DagRun information is serialized for OpenLineage events, the output is missing:
- `partition_key`: The partition identifier string (or None)
- `partition_date`: The partition date in ISO 8601 format (or None)

## Expected Behavior

The DagRun serialization must include these two fields. The source code controlling which fields are serialized uses entries with inline version comments in the pattern `"<field_name>",  # Airflow X.Y`. The new entries must satisfy:

1. **Field names**: The exact strings `"partition_key"` and `"partition_date"` must be included.
2. **Version comments**: Each entry must have a trailing inline comment with the exact text `# Airflow 3.2+`, matching the existing formatting convention (string value, comma, two spaces, version comment).
3. **Ordering**: The entries must appear after the `"logical_date"` entry (comment: `# Airflow 3`) and before the `"run_after"` entry (comment: `# Airflow 3`). `"partition_key"` must appear before `"partition_date"`.
4. **No duplicates**: Each field should appear only once.

All existing unit tests and linting (ruff, mypy) in the OpenLineage provider must continue to pass.

## Testing

You can run the relevant unit tests with:
```bash
cd providers/openlineage
uv run --group dev pytest tests/unit/openlineage/utils/test_utils.py -v
```
