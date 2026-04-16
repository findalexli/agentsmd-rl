# Task: Add Separate Affinity Settings for Kubernetes and Celery Workers

## Problem

The Airflow Helm chart currently uses a single `workers.affinity` configuration that applies to both Celery worker pods and Kubernetes executor pods (via the pod-template-file). Users cannot set different scheduling constraints for these two worker types.

For example, if a user wants Kubernetes executor pods to run on specific nodes (e.g., nodes with more memory for data processing tasks) while Celery workers should have different node affinity rules, they currently cannot achieve this with the existing configuration.

## What needs to change

The chart should support:
1. `workers.kubernetes.affinity` - affinity settings specifically for pods created via pod-template-file (Kubernetes executor)
2. `workers.celery.affinity` - affinity settings specifically for Celery worker pods

The precedence should be:
- For Kubernetes executor pods: `workers.kubernetes.affinity` > `workers.affinity` > `affinity`
- The existing `workers.affinity` should continue to work for backwards compatibility
- A deprecation warning should be shown when `workers.affinity` is used

## Files to investigate

- `chart/files/pod-template-file.kubernetes-helm-yaml` - Template for Kubernetes executor pods
- `chart/templates/workers/worker-deployment.yaml` - Celery worker deployment template
- `chart/values.yaml` - Default values
- `chart/values.schema.json` - JSON schema validation
- `chart/templates/NOTES.txt` - Installation notes and warnings

## Expected behavior

When rendering the chart with:
```yaml
workers:
  affinity:
    nodeAffinity: ...  # Legacy, should show deprecation warning
  kubernetes:
    affinity:
      nodeAffinity: ...  # Should be used for K8s executor pods
  celery:
    affinity:
      nodeAffinity: ...  # Should be used for Celery workers
```

The Kubernetes executor pods should use `workers.kubernetes.affinity`, and Celery workers should use `workers.celery.affinity`. If only `workers.affinity` is set, it should still work but display a deprecation warning.
