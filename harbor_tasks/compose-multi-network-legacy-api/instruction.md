# Restore multi-network compatibility with Docker API < 1.44

The repository under `/workspace/compose` is `docker/compose` (the Compose v2
CLI, written in Go). Recent refactoring of the moby client integration in
`pkg/compose/` introduced a regression for users running older Docker daemons.

## Symptom

When Compose deploys a service that attaches to **two or more networks**
against a Docker daemon advertising an API version **older than 1.44**
(for example Docker 20.10 / API 1.41 on Synology DSM 7.1, or DSM 7.2 on
API 1.43), the daemon rejects the request with:

```
Container cannot be connected to network endpoints
```

This used to work in earlier releases. Modern daemons (API >= 1.44) accept
multiple network endpoints in a single `ContainerCreate` call, but older
daemons accept **at most one** entry in the `EndpointsConfig` map and
require any further networks to be attached one-by-one via
`NetworkConnect` after the container has been created.

The current code in `pkg/compose/` always sends every network in the
initial create call, so on legacy daemons the request fails outright.

## What you need to do

Make Compose's container creation logic work correctly on Docker API
versions < 1.44 *without* regressing the modern path.

Concretely the runtime API version must be obtained (via the existing
`RuntimeAPIVersion` method on `composeService`), and:

1. When the negotiated API version is **>= 1.44**, behaviour must be
   unchanged: the create call continues to send the primary network plus
   every extra network in `EndpointsConfig` and no further connect calls
   are made.

2. When the negotiated API version is **< 1.44**:
   - The `ContainerCreate` request must include **only the primary
     network** (the one the service uses as `NetworkMode`) in
     `EndpointsConfig`. The other networks must be omitted from the
     create call.
   - After the container is created, every other network configured for
     the service must be attached individually with `NetworkConnect`,
     using endpoint settings produced by the existing
     `createEndpointSettings` helper. The primary network must be
     skipped (it is already attached).
   - If any of those `NetworkConnect` calls returns an error, the
     just-created (orphan) container must be removed with
     `ContainerRemove` using `Force: true`, and the original
     `NetworkConnect` error must be returned.
   - The post-create `ContainerInspect` (whose result populates the
     returned `container.Summary`) must run **after** the
     `NetworkConnect` loop, so the summary reflects every attached
     network.

The boundary value `1.44` is the API version introduced by Docker Engine
v25.0 (the first version whose `ContainerCreate` accepts multiple
`EndpointsConfig` entries). Define a single constant for it alongside the
other API-version constants the package already exposes, and reuse it from
both the create-time gate and the post-create fallback.

## Code Style Requirements

The repository enforces strict style rules via `golangci-lint` v2 (config
in `.golangci.yml`). Your changes must comply with all of them — the
benchmark verifies that:

- `gofmt -l pkg/compose` produces no output (gofumpt-compatible
  formatting).
- `go vet ./pkg/...` reports no issues.
- Imports follow the `gci`-enforced order: stdlib, then third-party,
  then this module's own packages (`github.com/docker/compose/v5/...`).
- No line exceeds **200 characters**.
- Cyclomatic complexity of any function stays below **16**.
- Do not introduce imports of `io/ioutil`, `github.com/pkg/errors`,
  `gopkg.in/yaml.v2`, `golang.org/x/exp/maps`, `golang.org/x/exp/slices`,
  or `github.com/docker/docker/errdefs` (use
  `github.com/containerd/errdefs` instead).

## Build & Test

- Compile the module: `go build ./...`
- Run the package's unit tests: `go test ./pkg/compose/...`

You should not need network access during the build or test phase — the
module cache is already populated.
