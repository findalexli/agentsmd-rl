# Add workers.celery.hpa configuration to Helm chart

## Problem

The Airflow Helm chart's HPA (Horizontal Pod Autoscaler) configuration for Celery workers is currently at `workers.hpa`. This is inconsistent with the pattern used for other Celery-specific settings, which are under `workers.celery.*`.

Users want to be able to configure HPA settings specifically for Celery workers using `workers.celery.hpa.*`, similar to how other Celery-specific settings are organized.

## Expected Behavior

1. A new `workers.celery.hpa` configuration section should be available with the same options as `workers.hpa`:
   - `enabled`
   - `minReplicaCount`
   - `maxReplicaCount`
   - `metrics`
   - `behavior`

2. Values set in `workers.celery.hpa.*` should override values in `workers.hpa.*`

3. The old `workers.hpa.*` path should continue to work for backward compatibility, but users should see deprecation warnings when using it

4. The `values.schema.json` should be updated to include the new configuration structure

## Files to Investigate

- `chart/values.yaml` - Default values configuration
- `chart/values.schema.json` - JSON schema for values validation
- `chart/templates/NOTES.txt` - Template for chart notes (deprecation warnings)
- `chart/templates/workers/worker-deployment.yaml` - Worker deployment template
- `chart/templates/workers/worker-hpa.yaml` - HPA template

## Notes

- The chart uses Helm templating with Go templates
- Ensure backward compatibility - existing `workers.hpa.*` configurations must continue to work
- Add appropriate deprecation warnings to guide users to the new configuration path
