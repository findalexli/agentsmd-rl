# EMR Serverless OpenLineage Integration Missing

When Airflow triggers an EMR Serverless Spark job using `EmrServerlessStartJobOperator`, the Spark job runs independently and emits its own OpenLineage events. However, there is no link back to the triggering Airflow task - the lineage chain is broken.

Other operators like `GlueJobOperator`, `SparkSubmitOperator`, `LivyOperator`, and `DataprocSubmitJobOperator` already support injecting OpenLineage parent job and transport information into their Spark configurations. EMR Serverless is missing this capability.

## The Problem

When `EmrServerlessStartJobOperator` starts a job, the resulting OpenLineage events from the Spark job cannot be correlated with the parent Airflow task run. Additionally, the Spark job may not know how to communicate with the OpenLineage backend that Airflow is using.

## What Needs to Happen

1. **Inject parent job information**: When enabled, the operator should inject OpenLineage parent job information (namespace, job name, run ID) into the EMR Serverless job configuration so the Spark job can emit a `parentRunFacet` linking back to the Airflow task.

2. **Inject transport information**: When enabled, the operator should inject OpenLineage transport configuration (backend URL, API key, etc.) into the EMR Serverless job configuration so the Spark job sends its OpenLineage events to the same backend as Airflow.

3. **Follow existing patterns**: The implementation should follow the same patterns used by other operators (GlueJobOperator, SparkSubmitOperator, etc.) that already support this feature.

## EMR Serverless Configuration Structure

EMR Serverless uses a nested configuration structure passed via `configuration_overrides`. Spark properties are configured under the `spark-defaults` classification:

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

## Expected Behavior

When the injection features are enabled:

1. The operator should accept optional boolean parameters to enable injection of parent job info and transport info (following the pattern of `openlineage.spark_inject_parent_job_info` and `openlineage.spark_inject_transport_info` config options)

2. If `configuration_overrides` is None, the injection should create the full nested structure

3. If `configuration_overrides` already contains an `applicationConfiguration` with a `spark-defaults` entry, the OpenLineage properties should be merged into its existing `properties` dict while preserving other properties

4. If OpenLineage properties are already present (e.g., `spark.openlineage.parentJobNamespace` already exists), injection should be skipped for that category

5. The original `configuration_overrides` dict should NOT be mutated - a new dict should be returned

6. The compat layer should export the new functions with fallback implementations that log warnings when OpenLineage is unavailable

## Where to Look

The OpenLineage utilities for Spark property injection are in the providers package. The compat layer for backward compatibility is also in the providers package. The `EmrServerlessStartJobOperator` is in the Amazon provider.

Look at how `GlueJobOperator` or `SparkSubmitOperator` implement similar functionality for reference - they use utility functions to inject OpenLineage information into their respective configuration formats.
