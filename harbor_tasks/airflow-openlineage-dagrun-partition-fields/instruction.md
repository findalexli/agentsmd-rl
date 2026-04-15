# Task: Add Partition Fields to OpenLineage DagRun Events

## Problem

Airflow 3.2 introduced `partition_key` and `partition_date` attributes on DagRun objects. The OpenLineage integration's DagRun serialization does not include these new fields when sending lineage events to backends.

## Symptom

The `DagRunInfo` class in the OpenLineage provider utils module controls which DagRun attributes are included in lineage events via its `includes` list. The attributes `partition_key` and `partition_date` are absent from this list, so partition information is dropped during serialization.

## Expected Behavior

Update the `DagRunInfo` class so that `partition_key` and `partition_date` are included in serialization output. The `includes` list entries follow a consistent version-comment convention — study the existing entries to determine the correct format and apply the appropriate version annotation for an Airflow 3.2 feature. Place the new entries in the appropriate position relative to surrounding entries, with each field appearing exactly once.

All existing unit tests and linting (ruff, mypy) in the OpenLineage provider must continue to pass.

## Testing

You can run the relevant unit tests with:
```bash
cd providers/openlineage
uv run --group dev pytest tests/unit/openlineage/utils/test_utils.py -v
```
