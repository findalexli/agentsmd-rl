# OpenLineage DagRunInfo Partition Fields

The OpenLineage provider's `DagRunInfo` class serializes DAG run information for lineage events. When a DAG has partition fields set (`partition_key` and `partition_date`), these must be included in the serialized output sent to the OpenLineage backend.

## Required Behavior

When serializing `DagRunInfo`, the output dictionary must include:

1. **`partition_key`** (string): The partition key associated with the DAG run
2. **`partition_date`** (string): The partition date in ISO 8601 format with timezone, e.g., `2024-06-01T00:00:00+00:00`

## Schema Requirements

The serialized output must contain these keys:
- `partition_key`: Must be a string value present in the output
- `partition_date`: Must be an ISO 8601 formatted datetime string with timezone suffix

## Ordering Requirements

The fields must appear in a specific order in the serialized output:
- `logical_date` must appear before `partition_key`
- `partition_key` must appear before `partition_date`
- `partition_date` must appear before `run_after`

This ordering reflects the temporal relationship: logical execution date → partition specification → when the run can execute after.

## DagRunInfo Class Requirement

The `DagRunInfo` class must include `partition_key` and `partition_date` in its `includes` list attribute. Each field must appear exactly once in this list.

## File Location

The relevant source file is:
`providers/openlineage/src/airflow/providers/openlineage/utils/utils.py`

The `DagRunInfo` class in this file handles serialization of DAG run information for OpenLineage events.

## Verification

You can verify the fix by running the OpenLineage provider unit tests:
```bash
cd providers/openlineage
uv run --group dev python -m pytest tests/unit/openlineage/utils/test_utils.py -v --tb=short
```

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `mypy (Python type checker)`
