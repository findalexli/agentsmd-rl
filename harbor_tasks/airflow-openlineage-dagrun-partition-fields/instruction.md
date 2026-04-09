# Task: Add Partition Fields to OpenLineage DagRun Events

## Problem

The OpenLineage integration in Airflow is missing `partition_key` and `partition_date` fields when serializing DagRun information. These fields were introduced in Airflow 3.2+ and need to be included in the OpenLineage events sent to lineage backends.

## Files to Modify

- `providers/openlineage/src/airflow/providers/openlineage/utils/utils.py`

## Expected Behavior

When DagRun information is serialized for OpenLineage events, the output should include:
- `partition_key`: The partition identifier string (or None)
- `partition_date`: The partition date in ISO 8601 format (or None)

## Where to Look

The `DagRunInfo` class in the utils file handles serialization of DagRun attributes. Look for the `attributes` class variable that defines which DagRun fields get serialized.

## Testing

The repo has existing unit tests in:
- `providers/openlineage/tests/unit/openlineage/utils/test_utils.py`

You can run tests with: `uv run --project providers/openlineage pytest <test_path>`

## Notes

- The fix involves adding two field names to a list of attributes
- The fields should be added with appropriate version comments (Airflow 3.2+)
- The serialization logic is already handled by the `InfoJsonEncodable` base class
