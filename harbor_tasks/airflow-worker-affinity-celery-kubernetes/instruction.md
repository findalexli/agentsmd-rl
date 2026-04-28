# Task: Add workers.celery.affinity and workers.kubernetes.affinity to Airflow Helm Chart

## Problem

The Airflow Helm chart currently has a single `workers.affinity` field that applies to both Celery workers and KubernetesExecutor pods. This design is problematic because:

1. Celery workers and KubernetesExecutor pods have different scheduling requirements
2. Users cannot configure different affinity rules for each type of worker
3. The single field conflates two distinct use cases

The `workers.affinity` field should be deprecated and replaced with two new fields:
- `workers.celery.affinity` - for Celery worker pods
- `workers.kubernetes.affinity` - for pods created via pod-template-file (KubernetesExecutor)

## Requirements

1. **New fields must work**: Setting `workers.celery.affinity` should apply to Celery worker deployments
2. **New fields must work**: Setting `workers.kubernetes.affinity` should apply to pod-template-file
3. **Backwards compatibility**: The old `workers.affinity` field must continue to work for both cases
4. **Precedence**: New specific fields should take precedence over the old field when both are set
5. **Deprecation warning**: NOTES.txt should warn users when `workers.affinity` is used, mentioning `workers.celery.affinity` and `workers.kubernetes.affinity` as alternatives
6. **Schema updates**: values.schema.json must include the new field definitions with `type: object` for both `workers.celery.affinity` and `workers.kubernetes.affinity`
7. **Deprecation documentation**: values.yaml should mark `workers.affinity` as deprecated and reference the new fields

## Files to Modify

- The pod template file used by KubernetesExecutor to create task pods (located under `chart/files/`)
- The Helm chart's post-install notes template (rendered after `helm install`)
- The chart's JSON schema file for validating values (used by `helm lint`)
- The chart's default values file that documents and provides initial values for all fields

Note: when adding new fields, you must update both the values file and the schema together, otherwise schema validation will fail. The pod template and notes template also need updates to wire up the new fields and deprecation warnings.

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
