# OpenLineage DagRunInfo Missing Partition Fields

## Problem

When Airflow DagRun objects with `partition_key` and `partition_date` attributes are serialized for OpenLineage events, these fields are missing from the output. OpenLineage consumers need access to this partition information from DAG runs.

## Context

Airflow 3.2+ introduced `partition_key` and `partition_date` attributes on DagRun objects. These represent the partition identifier and date for partitioned DAG runs.

OpenLineage integration in Airflow serializes DagRun information to JSON for emission as OpenLineage events via the `DagRunInfo` class in `providers/openlineage/src/airflow/providers/openlineage/utils/utils.py`. The `DagRunInfo` class inherits from `InfoJsonEncodable` and uses a class-level `includes` list to determine which fields are serialized.

## Expected Behavior

When a DagRun has `partition_key` and/or `partition_date` attributes set, those values must appear in the serialized output that is sent to OpenLineage consumers.

The serialized output is a JSON-compatible dictionary that should include:

- All standard DagRun fields: `dag_id`, `run_id`, `run_type`, `logical_date`, `execution_date`, `external_trigger`, `run_after`, `conf`, `clear_number`, `start_date`, `data_interval_start`, `data_interval_end`, `end_date`, `triggered_by`, `triggering_user_name`
- Plus the partition fields: `partition_key` and `partition_date`

When `partition_key` is set, it should appear in the output with its string value. When `partition_date` is set, it should appear as an ISO-formatted datetime string. When not set, both fields should appear as `None`.

## Files to Investigate

- `providers/openlineage/src/airflow/providers/openlineage/utils/utils.py` — contains the `DagRunInfo` class used for DagRun serialization
