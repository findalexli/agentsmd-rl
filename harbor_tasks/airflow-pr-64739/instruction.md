# Separate extraContainers for Celery and Kubernetes Workers

The Airflow Helm chart currently uses a single `workers.extraContainers` configuration to add sidecar containers to both Celery workers and Kubernetes executor pod templates. This causes confusion because:

1. Celery workers (deployed as StatefulSet/Deployment) and Kubernetes executor pods (created dynamically from pod-template-file) have different lifecycle requirements
2. Users often want different sidecars for each worker type
3. The current configuration doesn't make it clear which executor the containers apply to

## What needs to change

Add separate configuration paths:
- `workers.celery.extraContainers` - for Celery worker deployments
- `workers.kubernetes.extraContainers` - for pod-template-file (KubernetesExecutor)

The existing `workers.extraContainers` should continue to work for backward compatibility but should be deprecated with a warning.

## Files to investigate

- `chart/files/pod-template-file.kubernetes-helm-yaml` - Template for KubernetesExecutor pods
- `chart/values.yaml` - Default configuration values
- `chart/values.schema.json` - JSON schema for value validation
- `chart/templates/NOTES.txt` - Installation notes (for deprecation warnings)

## Requirements

1. The new `workers.kubernetes.extraContainers` should be used in pod-template-file when specified
2. If both old and new paths are specified, the new kubernetes-specific path takes priority
3. The legacy `workers.extraContainers` should still work as a fallback
4. A deprecation warning should appear when the legacy path is used
5. The JSON schema should be updated to include the new configuration options
6. Default values should be added for the new configuration paths
