# Task: Add workers.celery.serviceAccount & workers.kubernetes.serviceAccount

## Problem

The current Helm chart has a single `workers.serviceAccount` section that is used for both Celery workers and KubernetesExecutor pods. This doesn't allow users to configure separate ServiceAccounts for these different worker types, which is a common security requirement.

You need to split the `workers.serviceAccount` configuration into two new sections:
1. `workers.celery.serviceAccount` - for Celery workers
2. `workers.kubernetes.serviceAccount` - for KubernetesExecutor pods

The old `workers.serviceAccount` section should be deprecated but continue to work as a fallback for backward compatibility.

## Files to Modify

### Core Templates
- `chart/templates/_helpers.yaml` - Add support for nested service account sections (like `workers.kubernetes`) and new helper definitions
- `chart/templates/workers/worker-kubernetes-serviceaccount.yaml` - NEW FILE for kubernetes worker service account
- `chart/files/pod-template-file.kubernetes-helm-yaml` - Update to use workers.kubernetes.serviceAccount configuration
- `chart/templates/NOTES.txt` - Add deprecation warnings for old serviceAccount fields

### Configuration
- `chart/values.yaml` - Add new `workers.celery.serviceAccount` and `workers.kubernetes.serviceAccount` sections with these fields:
  - `automountServiceAccountToken` (nullable with `~` as default)
  - `create` (boolean)
  - `name` (string)
  - `annotations` (object, default `{}`)

- `chart/values.schema.json` - Add JSON schema definitions for the new sections with the same four properties listed above

### Documentation
- `chart/newsfragments/64730.significant.rst` - NEW FILE documenting the deprecation that must mention:
  - The deprecated `workers.serviceAccount` section
  - The new `workers.celery.serviceAccount` section
  - The new `workers.kubernetes.serviceAccount` section

## Requirements

### Helper Function Updates
The `_helpers.yaml` file needs logic to handle nested sections (e.g., `workers.kubernetes`). The existing `_serviceAccountName` helper must be enhanced to check for sub-sections.

You must create:
1. A core helper for generating service account names with support for nested configuration paths
2. A `worker.kubernetes.serviceAccountName` helper that uses the kubernetes-specific configuration

### Pod Template Updates
The `pod-template-file.kubernetes-helm-yaml` must conditionally use the kubernetes worker service account configuration:
- When `workers.kubernetes.serviceAccount.create` is enabled, use the kubernetes-specific service account
- Otherwise, fall back to the existing worker service account configuration

### Backward Compatibility
All new fields must fallback to the old `workers.serviceAccount` values when not explicitly set:
- `workers.kubernetes.serviceAccount.annotations` defaults to `workers.serviceAccount.annotations`
- `workers.kubernetes.serviceAccount.automountServiceAccountToken` defaults to `workers.serviceAccount.automountServiceAccountToken`

### Deprecation Warnings
Add warnings in NOTES.txt for these four deprecated fields:
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
