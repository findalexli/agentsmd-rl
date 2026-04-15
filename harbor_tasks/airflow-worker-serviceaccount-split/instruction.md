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

2. **`chart/templates/_helpers.yaml`** must contain:
   - A helper named `_serviceAccountNameGen` for generating service account names with support for nested configuration paths
   - A helper named `worker.kubernetes.serviceAccountName` that references the kubernetes-specific configuration
   - The existing `_serviceAccountName` helper must support a `.subKey` parameter to handle nested sections like `workers.kubernetes`

3. **`chart/files/pod-template-file.kubernetes-helm-yaml`** must:
   - Check for `.Values.workers.kubernetes.serviceAccount.create`
   - Use the `worker.kubernetes.serviceAccountName` helper when rendering service account names

4. **`chart/templates/NOTES.txt`** must include deprecation warnings for these four fields:
   - `workers.serviceAccount.automountServiceAccountToken`
   - `workers.serviceAccount.create`
   - `workers.serviceAccount.name`
   - `workers.serviceAccount.annotations`

### Backward Compatibility

When the new kubernetes-specific fields are not explicitly set, they must fallback to the old `workers.serviceAccount` values:
- `workers.kubernetes.serviceAccount.annotations` defaults to `workers.serviceAccount.annotations`
- `workers.kubernetes.serviceAccount.automountServiceAccountToken` defaults to `workers.serviceAccount.automountServiceAccountToken`

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
1. New templates and helpers exist with the exact names specified above
2. Schema and values are valid
3. Both celery and kubernetes service accounts render correctly
4. Backward compatibility with deprecated fields works
5. Deprecation warnings are present in NOTES.txt
6. The `_serviceAccountName` helper supports the `.subKey` parameter for nested configuration
