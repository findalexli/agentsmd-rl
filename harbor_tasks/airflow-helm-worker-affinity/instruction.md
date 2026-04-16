# Helm Chart: Separate Worker Affinity Configuration

## Problem

The Airflow Helm chart currently uses `workers.affinity` to configure scheduling constraints for both Celery workers and Kubernetes executor pods. However, users need the ability to configure different affinity rules for these two worker types independently.

When deploying Airflow with multiple executor types (like CeleryKubernetesExecutor), the Celery workers may need different node placement than the Kubernetes executor pods. The current single `workers.affinity` field doesn't support this use case.

## Expected Behavior

Users should be able to specify:
- `workers.celery.affinity` for Celery worker pods
- `workers.kubernetes.affinity` for pods created via the Kubernetes executor pod-template-file

These new fields should take precedence over the existing `workers.affinity` when specified, allowing fine-grained control while maintaining backward compatibility.

## Requirements

1. **Kubernetes executor affinity precedence**: When both `workers.kubernetes.affinity` and `workers.affinity` are set, the `workers.kubernetes.affinity` value must take precedence in the pod-template-file used by the Kubernetes executor. Currently, `workers.kubernetes.affinity` is ignored and only `workers.affinity` is used.

2. **Celery worker affinity**: Add support for `workers.celery.affinity` in worker deployments.

3. **Backward compatibility**: When only `workers.affinity` is set (without the new fields), it must continue to work for both Kubernetes executor pods and Celery workers.

4. **Deprecation warning in post-install notes**: The chart's NOTES.txt template must include a deprecation warning when `workers.affinity` is used. The warning logic should:
   - Check for usage of `.Values.workers.affinity` (non-empty)
   - Mention `workers.celery.affinity` and `workers.kubernetes.affinity` as the replacement fields

5. **JSON schema updates**: Update the values JSON schema to document the new fields:
   - Add a `workers.kubernetes.affinity` property with a description that references "kubernetes" or "pod-template-file"
   - Add a `workers.celery.affinity` property
   - The existing `helm lint`, chart schema validation, and JSON schema validation must continue to pass
