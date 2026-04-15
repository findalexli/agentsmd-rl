# Accept digest for init container image

## Problem

The Dagster Helm chart's `initContainers` configuration in `dagster-user-deployments` only supports specifying container images as strings (e.g., `image: "busybox:latest"`). When a user specifies an image as a structured object with `repository`, `tag`, or `digest` fields, the Helm template fails to render the correct image reference. Users need the ability to reference images by digest for immutable, verifiable deployments.

## Expected Behavior

The chart must support both string and structured image formats for init containers, with **backwards compatibility** for existing string-based configurations.

### Helm Template Rendering

When `helm template` renders a release, init containers should produce the following image strings:

| Input | Rendered `image` |
|---|---|
| `image: "busybox:latest"` (string) | `busybox:latest` |
| `image: {repository: "busybox", tag: "1.36"}` | `busybox:1.36` |
| `image: {repository: "busybox", digest: "sha256:abc123def456"}` | `busybox@sha256:abc123def456` |
| `image: {repository: "busybox", tag: "1.36", digest: "sha256:abc123def456"}` | `busybox@sha256:abc123def456` (digest takes precedence) |

When `pullPolicy` is specified in a structured image, it must be rendered as `imagePullPolicy` on the container.

Multiple init containers with mixed formats (string and structured) in a single deployment must all render correctly. For example, `alpine:3.18` (string) and `busybox@sha256:xyz789` (structured digest) must both render correctly when present in the same deployment.

### Python Schema Classes

The Python validation schema in `helm/dagster/schema/` uses Pydantic models to validate Helm values. The following classes must be added to `schema.charts.utils.kubernetes`:

**`InitContainerImage`** — A Pydantic model representing an image specification for init containers:
- Fields: `repository` (str, required), `tag` (optional str or int), `digest` (optional str), `pullPolicy` (optional)
- Must expose a `.name` property that returns the formatted image reference string:
  - When `digest` is set: `"{repository}@{digest}"` (digest takes precedence over tag)
  - When only `tag` is set: `"{repository}:{tag}"`
  - When neither is set: `"{repository}"`
- Example: `InitContainerImage(repository="busybox", tag="1.36").name` returns `"busybox:1.36"`
- Example: `InitContainerImage(repository="busybox", digest="sha256:abc123").name` returns `"busybox@sha256:abc123"`

**`InitContainerWithStructuredImage`** — A Pydantic model representing an init container with a structured image:
- Fields: `name` (str, required), `image` (InitContainerImage, required)
- Allows additional properties (extra="allow")
- Example: `InitContainerWithStructuredImage(name="init-test", image=init_img).image.name` returns the formatted image string

The `UserDeployment` model's `initContainers` field must accept both the existing `kubernetes.Container` type and the new `kubernetes.InitContainerWithStructuredImage` type.

### JSON Schema (values.schema.json)

Both `values.schema.json` files (the subchart at `helm/dagster/charts/dagster-user-deployments/values.schema.json` and the main chart at `helm/dagster/values.schema.json`) must be updated:

- Add a `$defs.InitContainerImage` definition with properties: `repository` (required string), `tag` (string, int, or null), `digest` (string or null), `pullPolicy` (PullPolicy ref or null)
- Add a `$defs.InitContainerWithStructuredImage` definition with properties: `name` (required string), `image` (required `$ref` to `InitContainerImage`), and `additionalProperties: true`
- Update the `UserDeployment.initContainers` property so its array items accept either the existing `Container` `$ref` or the new `InitContainerWithStructuredImage` `$ref`

### Helm Helper Templates

The `_helpers.tpl` file at `helm/dagster/charts/dagster-user-deployments/templates/helpers/_helpers.tpl` must define two new named templates:

- **`dagster.initContainerImage.name`** — Renders the image reference from either a string or structured format. Must use `kindIs "string"` to detect the legacy string format for backwards compatibility, and handle `$image.digest` for digest-based references.
- **`dagster.initContainer`** — Renders a full init container spec, processing the image field and forwarding `imagePullPolicy` when present.

The deployment template `deployment-user.yaml` must use these helpers by iterating over init containers with `range $container := $deployment.initContainers` and including the `"dagster.initContainer"` helper for each.

## Example values.yaml

```yaml
deployments:
  - name: "my-deployment"
    # ... other config
    initContainers:
      - name: init-legacy
        image: "busybox:latest"
        command: ["sh", "-c", "echo legacy"]

      - name: init-with-tag
        image:
          repository: "busybox"
          tag: "1.36"
        command: ["sh", "-c", "echo tag"]

      - name: init-with-digest
        image:
          repository: "busybox"
          digest: "sha256:abc123def456"
        command: ["sh", "-c", "echo digest"]

      - name: init-both
        image:
          repository: "busybox"
          tag: "1.36"
          digest: "sha256:abc123def456"
        command: ["sh", "-c", "echo both"]
```

Expected rendered images: `busybox:latest`, `busybox:1.36`, `busybox@sha256:abc123def456`, `busybox@sha256:abc123def456`.

## Codebase Context

The Dagster Helm chart is located at `helm/dagster/` within the repository. The `dagster-user-deployments` subchart is at `helm/dagster/charts/dagster-user-deployments/`.

Key files:
- `helm/dagster/schema/schema/charts/utils/kubernetes.py` — Pydantic models for Kubernetes resources (Image, Container, etc.)
- `helm/dagster/schema/schema/charts/dagster_user_deployments/subschema/user_deployments.py` — UserDeployment model
- `helm/dagster/charts/dagster-user-deployments/templates/helpers/_helpers.tpl` — Shared Helm template helpers
- `helm/dagster/charts/dagster-user-deployments/templates/deployment-user.yaml` — Deployment manifest template
- `helm/dagster/charts/dagster-user-deployments/values.schema.json` — Subchart JSON schema
- `helm/dagster/values.schema.json` — Main chart JSON schema

The existing chart already supports structured image formats for main containers — the init container configuration should follow similar patterns for consistency.

## Validation

The solution must satisfy all of the following:

1. **Helm template rendering**: `helm template` must correctly render init containers for all image format combinations (string, structured with tag, structured with digest, structured with both tag and digest)
2. **Python schema tests**: The existing test suite at `helm/dagster/schema/schema_tests/test_user_deployments.py` must pass
3. **Helm lint**: Both `helm lint --strict` on the subchart and `helm lint . --with-subcharts --strict` on the main chart must pass
4. **Ruff**: Python code in the schema directory must pass `ruff` linting
5. **All existing schema tests**: The full test suite (dagit, daemon, celery queues) at `helm/dagster/schema/schema_tests/` must continue to pass

## Testing

```bash
# Helm template rendering
cd helm/dagster/charts/dagster-user-deployments
helm template test-release . -f your-test-values.yaml

# Python schema tests
cd helm/dagster/schema
pytest schema_tests/test_user_deployments.py -v
```
