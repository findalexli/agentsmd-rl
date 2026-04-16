# Apache Airflow Helm Chart: Worker Service Account Configuration

## Problem

The Apache Airflow Helm chart currently uses a single `workers.serviceAccount` configuration section that applies to all worker types. This is problematic when deploying with `CeleryKubernetesExecutor` or when you need different service account configurations for Celery workers vs Kubernetes executor pod workers.

For example, you might want:
- Celery workers to use a service account with permissions to access certain AWS resources
- Kubernetes executor pods to use a different service account with permissions to spawn pods

Currently there's no way to configure these separately.

## Task

Add executor-specific service account configuration sections:
- `workers.celery.serviceAccount` for CeleryExecutor workers
- `workers.kubernetes.serviceAccount` for KubernetesExecutor pod workers

Each section should support the same options as the current `workers.serviceAccount`:
- `create`: Whether to create the service account (boolean)
- `name`: The name of the service account (string)
- `annotations`: Annotations to add to the service account (map)
- `automountServiceAccountToken`: Whether to automount the service account token (boolean)

The existing `workers.serviceAccount` should continue to work as a fallback for backward compatibility.

All worker service accounts created via these new sections must include the label `component: worker` in their metadata.

## Files to Modify

- `chart/values.yaml` - Add new configuration sections
- `chart/values.schema.json` - Add JSON schema for new options
- `chart/templates/_helpers.yaml` - Add helper functions for the new service accounts
- `chart/templates/workers/` - May need new templates for separate service accounts
- `chart/files/pod-template-file.kubernetes-helm-yaml` - Update to use new kubernetes service account

## Acceptance Criteria

1. Running `helm template` with `workers.kubernetes.serviceAccount.create=true` and `executor=KubernetesExecutor` creates a separate kubernetes worker ServiceAccount resource with the label `component: worker` in its metadata
2. Running `helm template` with `workers.celery.serviceAccount.create=true` and `executor=CeleryExecutor` creates a celery worker ServiceAccount resource with the specified name
3. Custom annotations set on `workers.kubernetes.serviceAccount.annotations` are applied to the rendered kubernetes worker ServiceAccount
4. Custom annotations set on `workers.celery.serviceAccount.annotations` are applied to the rendered celery worker ServiceAccount
5. Setting `workers.kubernetes.serviceAccount.automountServiceAccountToken=false` results in `automountServiceAccountToken: false` on the kubernetes worker ServiceAccount resource
6. The legacy `workers.serviceAccount` configuration continues to work — setting `workers.serviceAccount.create=true` and `workers.serviceAccount.name` should still create a ServiceAccount with that name (backward compatibility)
7. Running `helm template` with `executor=CeleryKubernetesExecutor` renders successfully without errors
8. `helm lint chart/` passes without errors
9. `python scripts/ci/prek/chart_schema.py` (chart schema validation script) exits with code 0
