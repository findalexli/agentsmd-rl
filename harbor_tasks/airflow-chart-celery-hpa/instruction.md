# Task: Add workers.celery.hpa Configuration to Airflow Helm Chart

## Problem

The Airflow Helm chart currently has HPA (Horizontal Pod Autoscaler) configuration under `workers.hpa`, but this doesn't align with the new Celery worker configuration structure. Users need a way to configure HPA under `workers.celery.hpa` while maintaining backward compatibility with the old `workers.hpa` path.

The chart should:
1. Support the new `workers.celery.hpa.*` configuration path
2. Keep the old `workers.hpa.*` path working (backward compatibility)
3. Mark the old path as deprecated in the JSON schema
4. Add deprecation warnings when old config is used (in NOTES.txt)

## Files to Modify

- `chart/values.yaml` - Add new `workers.celery.hpa` section with same structure as `workers.hpa`
- `chart/values.schema.json` - Add schema for `workers.celery.hpa`, update old `workers.hpa` descriptions with deprecation notes
- `chart/templates/NOTES.txt` - Add deprecation warnings for old `workers.hpa` usage
- `chart/templates/workers/worker-deployment.yaml` - Small fix: move `---` separator inside the Celery executor conditional
- `helm-tests/tests/helm_tests/airflow_core/test_worker.py` - Update tests to support both old and new config paths
- `helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py` - Update tests to support both old and new config paths
- `helm-tests/tests/helm_tests/other/test_hpa.py` - Update tests to support both old and new config paths
- `chart/newsfragments/64734.significant.rst` - Add newsfragment about the deprecation

## Expected Behavior

After the change:
- `workers.celery.hpa.enabled: true` should create an HPA resource
- `workers.hpa.enabled: true` should still work but be deprecated
- The HPA should be created for `CeleryExecutor` and `CeleryKubernetesExecutor`
- The HPA should NOT be created when KEDA is enabled (they're mutually exclusive)
- Schema descriptions should indicate which fields are deprecated

## Testing

Tests use Helm template rendering with jmespath queries to verify:
- HPA resources are created with correct configuration
- Scale target references match persistence settings
- Metrics, replica counts, and behavior are correctly applied
- Both old and new config paths work as expected

Run tests with: `pytest /tests/test_outputs.py -v`
