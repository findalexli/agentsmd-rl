# Task: Add workers.celery.serviceAccount & workers.kubernetes.serviceAccount

## Problem

The current Helm chart has a single `workers.serviceAccount` section that is used for both Celery workers and KubernetesExecutor pods. This doesn't allow users to configure separate ServiceAccounts for these different worker types, which is a common security requirement.

The chart should support separate service account configuration for each worker type while maintaining backward compatibility with the existing configuration.

## Requirements

### Configuration Structure

Add new configuration sections in `chart/values.yaml`:

1. **`workers.celery.serviceAccount`** - for Celery workers with these fields:
   - `automountServiceAccountToken` (nullable with `~` as default)
   - `create` (boolean)
   - `name` (string)
   - `annotations` (object, default `{}`)

2. **`workers.kubernetes.serviceAccount`** - for KubernetesExecutor pods with the same four fields:
   - `automountServiceAccountToken` (nullable with `~` as default)
   - `create` (boolean)
   - `name` (string)
   - `annotations` (object, default `{}`)

These same four properties must also be defined in `chart/values.schema.json` under the respective sections.

### Template Files

The following template files must be created or modified:

1. **NEW FILE: `chart/templates/workers/worker-kubernetes-serviceaccount.yaml`**
   - Must define a ServiceAccount resource for Kubernetes executor pods
   - This ServiceAccount should be created when using KubernetesExecutor and workers.kubernetes.serviceAccount.create is true

2. **`chart/templates/_helpers.yaml`** must be updated to:
   - Add a new `_serviceAccountNameGen` helper function that generates service account names based on `create` flag, `name`, and a `key`/`nameSuffix`
   - Refactor the existing `_serviceAccountName` helper to accept an optional `.subKey` parameter for nested configuration paths (like `workers.kubernetes`)
   - Add a new `worker.kubernetes.serviceAccountName` helper that calls `_serviceAccountName` with `key="workers"`, `subKey="kubernetes"`, and `nameSuffix="worker-kubernetes"`

3. **`chart/files/pod-template-file.kubernetes-helm-yaml`** must:
   - Check for `.Values.workers.kubernetes.serviceAccount.create`
   - Use the `worker.kubernetes.serviceAccountName` helper (from `_helpers.yaml`) when rendering service account names for pods

4. **`chart/templates/NOTES.txt`** must include deprecation warnings for these four fields:
   - `workers.serviceAccount.automountServiceAccountToken`
   - `workers.serviceAccount.create`
   - `workers.serviceAccount.name`
   - `workers.serviceAccount.annotations`

### Backward Compatibility

When the new kubernetes-specific fields are not explicitly set, they must fallback to the old `workers.serviceAccount` values:
- `workers.kubernetes.serviceAccount.annotations` defaults to `workers.serviceAccount.annotations`
- `workers.kubernetes.serviceAccount.automountServiceAccountToken` defaults to `workers.serviceAccount.automountServiceAccountToken`
- The Celery worker service account should continue to use the existing worker service account helper

### Documentation

**NEW FILE: `chart/newsfragments/64730.significant.rst`** must document the change and mention:
- The deprecated `workers.serviceAccount` section
- The new `workers.celery.serviceAccount` section
- The new `workers.kubernetes.serviceAccount` section

## Testing

Run the Helm tests to verify your changes:
```bash
cd /workspace/airflow
helm lint chart
helm template test-release chart
```

The tests will verify:
1. New templates exist and render correctly
2. Schema and values are valid
3. Both celery and kubernetes service accounts render correctly with custom names and annotations
4. Backward compatibility with deprecated fields works (when new fields aren't set, old values are used)
5. Deprecation warnings are present in NOTES.txt
6. The pod-template-file correctly uses the kubernetes service account when configured
