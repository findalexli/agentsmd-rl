# Airflow Helm Chart: Executor-Specific Extra Containers

## Problem

The Airflow Helm chart currently uses a single `workers.extraContainers` configuration for adding sidecar containers to worker pods. This works but is problematic because:

1. **Celery workers** (StatefulSet/Deployment) and **KubernetesExecutor pod templates** have different lifecycle requirements
2. Users want to configure different sidecars for different executor types
3. The single config path forces the same containers on both executor types

## Expected Behavior

Users should be able to configure executor-specific extra containers:
- `workers.kubernetes.extraContainers` for KubernetesExecutor pod templates
- `workers.celery.extraContainers` for Celery worker deployments

When the executor-specific config is set, it should take precedence. The existing `workers.extraContainers` should continue working for backward compatibility but should be marked as deprecated.

## Files to Investigate

- `chart/files/pod-template-file.kubernetes-helm-yaml` - Pod template for KubernetesExecutor
- `chart/values.yaml` - Default values with config structure
- `chart/values.schema.json` - JSON Schema validation
- `chart/templates/NOTES.txt` - User-facing notes (for deprecation warning)

## Requirements

1. Add `workers.kubernetes.extraContainers` to values.yaml and schema
2. Add `workers.celery.extraContainers` to values.yaml and schema
3. Update pod-template-file.kubernetes-helm-yaml to use the new kubernetes-specific path
4. Ensure the new path takes precedence when both old and new are set
5. Add deprecation notice for the old `workers.extraContainers` path
