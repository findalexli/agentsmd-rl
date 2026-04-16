# EMR Serverless OpenLineage Integration Missing

When Airflow triggers an EMR Serverless Spark job using `EmrServerlessStartJobOperator`, the Spark job runs independently and emits its own OpenLineage events. However, there is no link back to the triggering Airflow task - the lineage chain is broken.

Other operators like `GlueJobOperator`, `SparkSubmitOperator`, `LivyOperator`, and `DataprocSubmitJobOperator` already support injecting OpenLineage parent job and transport information into their Spark configurations. EMR Serverless is missing this capability.

## The Problem

The OpenLineage utilities in `providers/openlineage/src/airflow/providers/openlineage/utils/spark.py` lack functions to inject OpenLineage configuration into EMR Serverless job configurations. Additionally, the `EmrServerlessStartJobOperator` in `providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py` cannot access these utilities from the compat layer at `providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py`.

Specifically, the following functions need to be implemented:

1. **`inject_parent_job_information_into_emr_serverless_properties(configuration_overrides, context)`** - Injects OpenLineage parent job information (namespace, job name, run ID) into the EMR Serverless `spark-defaults` configuration. The function should:
   - Accept `configuration_overrides` (dict or None) and `context` parameters
   - Return a new dict with the nested `applicationConfiguration` structure updated
   - NOT mutate the original `configuration_overrides` dict
   - Skip injection if `spark.openlineage.parentJobNamespace` is already present in properties

2. **`inject_transport_information_into_emr_serverless_properties(configuration_overrides, context)`** - Injects OpenLineage transport configuration so the Spark job sends events to the same backend as Airflow. The function should:
   - Accept `configuration_overrides` (dict or None) and `context` parameters
   - Return a new dict with the nested `applicationConfiguration` structure updated
   - Skip injection if `spark.openlineage.transport.type` is already present in properties

3. **`_get_or_create_spark_defaults_properties(configuration_overrides)`** - A helper function that:
   - Locates or creates the `spark-defaults` entry within `applicationConfiguration`
   - Returns the `properties` dict of the `spark-defaults` entry
   - Creates the full nested structure if `applicationConfiguration` doesn't exist

## Expected Configuration Schema

EMR Serverless uses a nested configuration structure. The `configuration_overrides` dict has this schema:

```python
{
    "applicationConfiguration": [
        {
            "classification": "spark-defaults",
            "properties": {
                "spark.openlineage.parentJobNamespace": "<namespace>",
                "spark.openlineage.parentJobName": "<job_name>",
                "spark.openlineage.parentRunId": "<run_id>",
                "spark.openlineage.transport.type": "http",
                "spark.openlineage.transport.url": "<url>",
                # ... other spark properties
            }
        },
        # ... other classifications like spark-env
    ],
    "monitoringConfiguration": {
        # preserved as-is
    }
}
```

Key requirements:
- The `applicationConfiguration` key maps to a list of configuration entries
- Each entry has a `"classification"` string key and a `"properties"` dict key
- The `"spark-defaults"` classification is where Spark properties are configured
- Other configuration keys like `monitoringConfiguration` must be preserved
- Property keys for OpenLineage follow the pattern `spark.openlineage.*`

## Required Integration Points

1. **OpenLineage spark utilities** (`providers/openlineage/src/airflow/providers/openlineage/utils/spark.py`):
   - Implement the three functions above
   - Follow the pattern of existing functions like `inject_parent_job_information_into_spark_properties`
   - Reuse existing helpers `_get_parent_job_information_as_spark_properties`, `_get_transport_information_as_spark_properties`, `_is_parent_job_information_present_in_spark_properties`, and `_is_transport_information_present_in_spark_properties`

2. **Compat layer** (`providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py`):
   - Export the new EMR Serverless functions
   - Add them to the `__all__` list
   - Provide fallback implementations that log warnings when OpenLineage is unavailable

3. **EMR Serverless operator** (`providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py`):
   - Import the new functions from the compat layer
   - Add optional boolean parameters `openlineage_inject_parent_job_info` and `openlineage_inject_transport_info`
   - When enabled, call the injection functions in the `execute` method before starting the job
   - Use the modified `configuration_overrides` when calling the EMR Serverless API

## Files to Modify

- `providers/openlineage/src/airflow/providers/openlineage/utils/spark.py` - Add the three EMR Serverless injection functions
- `providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py` - Export the new functions with fallback implementations
- `providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py` - Integrate the injection into `EmrServerlessStartJobOperator`
