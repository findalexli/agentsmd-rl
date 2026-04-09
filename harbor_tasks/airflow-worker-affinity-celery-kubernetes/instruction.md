# Task: Add workers.celery.affinity and workers.kubernetes.affinity to Airflow Helm Chart

## Problem

The Airflow Helm chart currently has a single `workers.affinity` field that applies to both Celery workers and KubernetesExecutor pods. This design is problematic because:

1. Celery workers and KubernetesExecutor pods have different scheduling requirements
2. Users cannot configure different affinity rules for each type of worker
3. The single field conflates two distinct use cases

The `workers.affinity` field needs to be deprecated and replaced with two new fields:
- `workers.celery.affinity` - for Celery worker pods
- `workers.kubernetes.affinity` - for pods created via pod-template-file (KubernetesExecutor)

## Files to Modify

### chart/files/pod-template-file.kubernetes-helm-yaml
This template file is used by KubernetesExecutor to create task pods. The affinity logic needs to be updated to check for `workers.kubernetes.affinity` first, falling back to the deprecated `workers.affinity` for backwards compatibility.

### chart/templates/NOTES.txt
Add a deprecation warning that appears when users have set the old `workers.affinity` field, directing them to use the new fields instead.

### chart/values.schema.json
Add JSON schema definitions for the new `workers.celery.affinity` and `workers.kubernetes.affinity` fields. Update the description of the deprecated `workers.affinity` field to indicate it's deprecated.

### chart/values.yaml
Add the new `affinity: {}` fields under both `workers.celery` and `workers.kubernetes` sections. Add deprecation comments to the old `workers.affinity` field.

### Test files (optional, if needed)
The existing tests are in:
- `helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py`
- `helm-tests/tests/helm_tests/airflow_core/test_worker.py`
- `helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py`

These tests use `render_chart()` and `jmespath` to verify rendered Helm templates.

## Requirements

1. **New fields must work**: Setting `workers.celery.affinity` should apply to Celery worker deployments
2. **New fields must work**: Setting `workers.kubernetes.affinity` should apply to pod-template-file
3. **Backwards compatibility**: The old `workers.affinity` field must continue to work for both cases
4. **Precedence**: New specific fields should take precedence over the old field when both are set
5. **Deprecation warning**: NOTES.txt should warn users when `workers.affinity` is used
6. **Schema updates**: values.schema.json must include the new field definitions

## Testing

You can test your changes using Helm commands:

```bash
# Test pod template rendering
helm template test-release chart/ --show-only templates/pod-template-file.yaml \
  --set workers.kubernetes.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key=test \
  --set workers.kubernetes.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].operator=In \
  --set workers.kubernetes.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].values[0]=value

# Test worker deployment rendering
helm template test-release chart/ --show-only templates/workers/worker-deployment.yaml \
  --set workers.celery.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key=test
```

The repo has a test suite in the `helm-tests/` directory that you can run with pytest.

## Hints

- Look at how `workers.kubernetes.nodeSelector` and `workers.celery.nodeSelector` are implemented for a similar pattern
- The `or` function in Helm templates evaluates left-to-right and returns the first non-empty value
- The pod-template-file template is at `chart/files/pod-template-file.kubernetes-helm-yaml` (note: it's a template file used by Helm, but not rendered as part of `helm template` output directly - it's used at runtime by KubernetesExecutor)
- Check the existing `workers.kubernetes.priorityClassName` and `workers.celery.priorityClassName` pattern
