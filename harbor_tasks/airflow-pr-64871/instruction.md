# Add workers.celery.hpa configuration to Helm chart

## Problem

The Airflow Helm chart's HPA (Horizontal Pod Autoscaler) configuration for Celery workers is currently at `workers.hpa`. This is inconsistent with the pattern used for other Celery-specific settings, which are under `workers.celery.*`.

Users want to be able to configure HPA settings specifically for Celery workers using `workers.celery.hpa.*`, similar to how other Celery-specific settings are organized.

## Expected Behavior

1. A new `workers.celery.hpa` configuration section should be available with these options:
   - `enabled` (boolean)
   - `minReplicaCount` (integer)
   - `maxReplicaCount` (integer)
   - `metrics` (array)
   - `behavior` (object)

2. Values set in `workers.celery.hpa.*` should override values in `workers.hpa.*`

3. The old `workers.hpa.*` path should continue to work for backward compatibility, but users should see deprecation warnings when using it

4. The `values.schema.json` should be updated to include the new configuration structure

## Files to Modify

- `chart/values.yaml` — add the new `workers.celery.hpa` section with the 5 options above
- `chart/values.schema.json` — add schema for `workers.celery.hpa`
- `chart/templates/NOTES.txt` — add deprecation warnings for old `workers.hpa.*` usage
- Helm templates under `chart/templates/workers/` may need updates to support the new config path

## Notes

- The chart uses Helm templating with Go templates
- Ensure backward compatibility - existing `workers.hpa.*` configurations must continue to work
- Add appropriate deprecation warnings to guide users to the new configuration path
