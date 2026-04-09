# Task: Add workers.celery.serviceAccount & workers.kubernetes.serviceAccount

## Problem

The current Helm chart has a single `workers.serviceAccount` section that is used for both Celery workers and KubernetesExecutor pods. This doesn't allow users to configure separate ServiceAccounts for these different worker types, which is a common security requirement.

You need to split the `workers.serviceAccount` configuration into two new sections:
1. `workers.celery.serviceAccount` - for Celery workers
2. `workers.kubernetes.serviceAccount` - for KubernetesExecutor pods

The old `workers.serviceAccount` section should be deprecated but continue to work as a fallback for backward compatibility.

## Files to Modify

### Core Templates
- `chart/templates/_helpers.yaml` - Add new helper functions for generating service account names with subKey support
- `chart/templates/workers/worker-kubernetes-serviceaccount.yaml` - NEW FILE for kubernetes worker service account
- `chart/files/pod-template-file.kubernetes-helm-yaml` - Update to conditionally use kubernetes service account
- `chart/templates/NOTES.txt` - Add deprecation warnings

### Configuration
- `chart/values.yaml` - Add new `workers.celery.serviceAccount` and `workers.kubernetes.serviceAccount` sections with proper defaults (~ for nullable, {} for annotations)
- `chart/values.schema.json` - Add JSON schema definitions for the new sections

### Documentation
- `chart/newsfragments/64730.significant.rst` - NEW FILE documenting the deprecation

### Tests (already exist in repo)
- `helm-tests/tests/helm_tests/airflow_aux/test_annotations.py`
- `helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py`
- `helm-tests/tests/helm_tests/airflow_core/test_worker.py`
- `helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py`

## Key Implementation Details

### Helper Function Pattern
The `_serviceAccountName` helper needs to be refactored to support a `subKey` parameter for nested sections like `workers.kubernetes`. Create a new `_serviceAccountNameGen` helper for the core logic.

Add a new `worker.kubernetes.serviceAccountName` helper that uses the subKey pattern:
```yaml
{{- define "worker.kubernetes.serviceAccountName" -}}
  {{- include "_serviceAccountName" (merge (dict "key" "workers" "subKey" "kubernetes" "nameSuffix" "worker-kubernetes") .) -}}
{{- end }}
```

### Service Account Selection Logic
In `pod-template-file.kubernetes-helm-yaml`, use conditional logic:
- If `workers.kubernetes.serviceAccount.create` is true, use `worker.kubernetes.serviceAccountName`
- Otherwise, fall back to the existing `worker.serviceAccountName`

### Backward Compatibility
All new fields must fallback to the old `workers.serviceAccount` values when not explicitly set:
- `workers.kubernetes.serviceAccount.annotations` defaults to `workers.serviceAccount.annotations`
- `workers.kubernetes.serviceAccount.automountServiceAccountToken` defaults to `workers.serviceAccount.automountServiceAccountToken`

### Deprecation Warnings
Add warnings in NOTES.txt for all four deprecated fields:
- `workers.serviceAccount.automountServiceAccountToken`
- `workers.serviceAccount.create`
- `workers.serviceAccount.name`
- `workers.serviceAccount.annotations`

## Testing

Run the Helm tests to verify your changes:
```bash
cd /workspace/airflow
helm lint chart
helm template test-release chart
```

The tests will verify:
1. New templates and helpers exist
2. Schema and values are valid
3. Both celery and kubernetes service accounts render correctly
4. Backward compatibility with deprecated fields works
5. Deprecation warnings are present
