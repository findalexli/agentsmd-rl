# Add OpenLineage Parent and Transport Info Injection to EMR Serverless Operator

## Problem

When Airflow triggers an EMR Serverless Spark job via `EmrServerlessStartJobOperator`, the job runs independently and emits its own OpenLineage events with no link back to the triggering Airflow task. Other similar operators like `GlueJobOperator`, `SparkSubmitOperator`, `LivyOperator`, and `DataprocSubmitJobOperator` already support injecting OpenLineage parent job information and transport configuration into their respective job configurations.

## Your Task

Add OpenLineage parent job and transport information injection capabilities to `EmrServerlessStartJobOperator`, following the same pattern used by other operators in the Airflow providers.

## Key Files to Modify

1. **`providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py`**
   - Add new boolean parameters to `EmrServerlessStartJobOperator`:
     - `openlineage_inject_parent_job_info` - injects `spark.openlineage.parent*` properties
     - `openlineage_inject_transport_info` - injects `spark.openlineage.transport.*` properties
   - Both should default to the existing Airflow config values (`openlineage.spark_inject_parent_job_info` and `openlineage.spark_inject_transport_info`, defaulting to `False` if unset)
   - Modify the `execute()` method to call the appropriate injection functions when these flags are enabled

2. **`providers/openlineage/src/airflow/providers/openlineage/utils/spark.py`**
   - Add helper function `_get_or_create_spark_defaults_properties()` to find or create the `spark-defaults` classification entry in EMR Serverless configuration overrides
   - Add `inject_parent_job_information_into_emr_serverless_properties()` function
   - Add `inject_transport_information_into_emr_serverless_properties()` function
   - These should follow the same pattern as the existing `inject_*_into_glue_arguments()` and `inject_*_into_spark_properties()` functions

3. **`providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py`**
   - Add fallback implementations for the new injection functions (for when openlineage provider is not installed)
   - Update `__all__` exports list

## Expected Behavior

When `openlineage_inject_parent_job_info=True`:
- The operator should inject `spark.openlineage.parentJobNamespace`, `spark.openlineage.parentJobName`, and `spark.openlineage.parentRunId` properties into the EMR Serverless `spark-defaults` configuration
- If these properties already exist, the injection should be skipped (idempotent)

When `openlineage_inject_transport_info=True`:
- The operator should inject `spark.openlineage.transport.type`, `spark.openlineage.transport.url`, etc. properties into the EMR Serverless `spark-defaults` configuration
- If transport properties already exist, the injection should be skipped (idempotent)

The functions should:
- Handle `None` input for `configuration_overrides` by creating a new structure
- Preserve any existing configuration (e.g., `monitoringConfiguration`, existing `spark-defaults` properties)
- Not mutate the input dictionary (create a copy before modifying)

## Reference

Look at how `GlueJobOperator` and other operators implement similar functionality:
- `inject_parent_job_information_into_glue_arguments()`
- `inject_transport_information_into_glue_arguments()`
- The EMR Serverless configuration structure is:
  ```python
  {
      "applicationConfiguration": [
          {"classification": "spark-defaults", "properties": {...}},
          ...
      ],
      "monitoringConfiguration": {...}
  }
  ```

## Testing

The implementation should allow the operator to work with both new flags enabled, disabled, or with default values. The injection functions should properly handle various edge cases including empty configs, existing spark-defaults entries, and other classification types.
