# Task: Add workers.celery.extraContainers & workers.kubernetes.extraContainers

## Problem

The Airflow Helm chart currently has a single `workers.extraContainers` field that is used for both Celery workers and Kubernetes executor pods. This is confusing because:

1. Users may want different sidecar containers for Celery workers vs Kubernetes executor pods
2. The current single field doesn't allow for this differentiation

You need to split this into two separate, more specific fields:
- `workers.celery.extraContainers` - for Celery worker deployments
- `workers.kubernetes.extraContainers` - for pod template file (Kubernetes executor)

The old `workers.extraContainers` field should be deprecated but continue to work for backward compatibility (when the new fields aren't set, the old one should still be used).

## Files to Modify

1. **`chart/values.yaml`** - Add the two new fields with empty list defaults and update the deprecated field's comment
2. **`chart/values.schema.json`** - Add JSON schema definitions for the two new fields and update the deprecated field's description
3. **`chart/files/pod-template-file.kubernetes-helm-yaml`** - Update to use `workers.kubernetes.extraContainers` with fallback to the deprecated `workers.extraContainers`
4. **`chart/templates/NOTES.txt`** - Add a deprecation warning when the old field is used
5. **`chart/newsfragments/64739.significant.rst`** - Create newsfragment about the deprecation
6. **`chart/docs/using-additional-containers.rst`** - Update documentation to show the new usage

## What Success Looks Like

The Helm chart should:
1. Accept `workers.celery.extraContainers` for Celery worker deployments
2. Accept `workers.kubernetes.extraContainers` for Kubernetes executor pod templates
3. Still accept `workers.extraContainers` for backward compatibility (but it's deprecated)
4. When both old and new fields are set, the new field takes precedence
5. Show a deprecation warning in NOTES.txt when the old field is used
6. Pass all existing helm tests plus new parametrized tests for both paths

## Testing

You can run the tests with pytest:
```bash
pytest helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py -v
pytest helm-tests/tests/helm_tests/airflow_core/test_worker.py -v
```

The key test scenarios are:
- Setting only `workers.kubernetes.extraContainers` renders containers in pod template
- Setting only `workers.extraContainers` (deprecated) still renders containers (backward compat)
- Setting both should use the new path
- Same scenarios for Celery workers in worker-deployment.yaml

## Repository Structure

- `chart/` - Helm chart files
  - `values.yaml` - Default values
  - `values.schema.json` - JSON schema for validation
  - `files/` - Raw files including pod template
  - `templates/` - Helm templates including NOTES.txt
  - `docs/` - Documentation
  - `newsfragments/` - News fragments for significant changes
- `helm-tests/` - Python tests for the Helm chart
