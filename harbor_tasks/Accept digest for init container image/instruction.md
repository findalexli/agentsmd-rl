# Accept digest for init container image

## Problem

The Dagster Helm chart's `initContainers` configuration currently only supports specifying container images as strings (e.g., `"busybox:latest"`). Users need the ability to specify images by digest instead of tag, which provides a more specific, immutable reference to a container image.

## Required Changes

You need to modify the Dagster Helm chart to support a structured image format for init containers that allows specifying:
- `repository` (required): The image repository
- `tag` (optional): The image tag
- `digest` (optional): The image digest (e.g., `sha256:abc123...`)
- `pullPolicy` (optional): The image pull policy

The change must be **backwards compatible** - existing deployments using the string format (e.g., `image: "busybox:latest"`) must continue to work.

When both `tag` and `digest` are specified, `digest` should take precedence since it is a more specific pointer.

## Files to Modify

1. **`helm/dagster/charts/dagster-user-deployments/templates/helpers/_helpers.tpl`**
   - Add a helper template `dagster.initContainerImage.name` to render image names from structured or string format
   - Add a helper template `dagster.initContainer` to process init container specs

2. **`helm/dagster/charts/dagster-user-deployments/templates/deployment-user.yaml`**
   - Update the initContainers section to use the new helper template

3. **`helm/dagster/charts/dagster-user-deployments/values.schema.json`**
   - Add `InitContainerImage` schema definition
   - Add `InitContainerWithStructuredImage` schema definition
   - Update the `initContainers` property in `UserDeployment` to accept both `Container` and `InitContainerWithStructuredImage`

4. **`helm/dagster/charts/dagster-user-deployments/values.yaml`**
   - Add documentation comments showing the new structured format

5. **`helm/dagster/schema/schema/charts/utils/kubernetes.py`**
   - Add `InitContainerImage` Pydantic model with a `name` property
   - Add `InitContainerWithStructuredImage` Pydantic model

6. **`helm/dagster/schema/schema/charts/dagster_user_deployments/subschema/user_deployments.py`**
   - Update the `initContainers` field type to include `InitContainerWithStructuredImage`

7. **`helm/dagster/values.schema.json`**
   - Same schema changes as the subchart

8. **`helm/dagster/schema/schema_tests/test_user_deployments.py`**
   - Add tests for the new init container functionality

## Expected Behavior

Given this values.yaml:

```yaml
deployments:
  - name: "my-deployment"
    # ... other config
    initContainers:
      # Legacy string format (backwards compatible)
      - name: init-legacy
        image: "busybox:latest"
        command: ["sh", "-c", "echo legacy"]
      
      # New structured format with tag
      - name: init-with-tag
        image:
          repository: "busybox"
          tag: "1.36"
        command: ["sh", "-c", "echo tag"]
      
      # New structured format with digest
      - name: init-with-digest
        image:
          repository: "busybox"
          digest: "sha256:abc123def456"
        command: ["sh", "-c", "echo digest"]
      
      # Both tag and digest (digest takes precedence)
      - name: init-both
        image:
          repository: "busybox"
          tag: "1.36"
          digest: "sha256:abc123def456"
        command: ["sh", "-c", "echo both"]
```

The rendered init containers should have images:
- `busybox:latest`
- `busybox:1.36`
- `busybox@sha256:abc123def456`
- `busybox@sha256:abc123def456` (digest wins)

## Testing

You can test your changes by running:

```bash
cd helm/dagster/charts/dagster-user-deployments
helm template test-release . -f your-test-values.yaml
```

The tests in `schema_tests/test_user_deployments.py` can be run with:

```bash
cd helm/dagster/schema
pytest schema_tests/test_user_deployments.py -v
```

## Reference

- Helm template functions: https://helm.sh/docs/chart_template_guide/function_list/
- Sprig template functions (included with Helm): http://masterminds.github.io/sprig/
- Dagster Helm chart structure: See existing helpers in `_helpers.tpl`
