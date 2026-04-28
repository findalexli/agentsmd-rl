#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kuma

# Idempotency guard
if grep -qF "k3d init containers sometimes get throttled on local machines. Set `K3D_HELM_DEP" ".claude/rules/debug.md" && grep -qF "`make check` runs `check/rbac`: if any RBAC manifests in `deployments/` change (" ".claude/rules/linting.md" && grep -qF "`make generate` runs per policy: `policy-gen core-resource` \u2192 `k8s-resource` \u2192 `" ".claude/rules/policies.md" && grep -qF "- Update deps: `gh workflow run update-insecure-dependencies.yaml --repo kumahq/" ".claude/rules/release.md" && grep -qF "Hand-written stubs only, no mockgen or counterfeiter. Implement the minimal inte" ".claude/rules/testing.md" && grep -qF "Run `make generate` after changes to `.proto` files, `pkg/plugins/policies/*/api" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/debug.md b/.claude/rules/debug.md
@@ -0,0 +1,110 @@
+# Debugging and local development
+
+## k3d cluster setup
+
+```bash
+make k3d/start KIND_CLUSTER_NAME=kuma-1
+export KUBECONFIG=~/.kube/kind-kuma-1-config
+```
+
+Kubeconfig: `~/.kube/kind-<name>-config`. k3d context: `k3d-<name>`.
+
+### Build, load, and deploy
+
+```bash
+# One step: build images, load into k3d, clean previous release, helm install, wait for CP
+make k3d/deploy/helm KIND_CLUSTER_NAME=kuma-1
+
+# Or step by step:
+make k3d/load KIND_CLUSTER_NAME=kuma-1
+make k3d/deploy/helm/upgrade k3d/deploy/wait/cp KIND_CLUSTER_NAME=kuma-1
+```
+
+### Variables
+
+| Variable | Default | Purpose |
+|:---------|:--------|:--------|
+| `KIND_CLUSTER_NAME` | `kuma` | Cluster name |
+| `KUMA_MODE` | `zone` | `zone` or `global` |
+| `K3D_HELM_DEPLOY_NO_CNI` | unset | Set `true` to skip CNI (lighter for local dev) |
+| `K3D_HELM_DEPLOY_ADDITIONAL_SETTINGS` | unset | Extra helm values, space-separated |
+| `K3D_DEPLOY_HELM_DONT_CLEAN` | unset | Set to skip cleaning previous release |
+
+### Deploy with custom settings
+
+```bash
+make k3d/deploy/helm KIND_CLUSTER_NAME=kuma-1 \
+  K3D_HELM_DEPLOY_NO_CNI=true \
+  K3D_HELM_DEPLOY_ADDITIONAL_SETTINGS="dataPlane.features.unifiedResourceNaming=true"
+```
+
+Other targets: `k3d/deploy/kumactl` (deploy via CLI), `k3d/deploy/demo` (demo app), `k3d/stop` (delete cluster).
+
+Renamed targets that will error: `k3d/restart` (use `k3d/restart/kumactl`), `k3d/deploy/kuma` (use `k3d/deploy/kumactl`).
+
+### Skaffold dev loop
+
+Hot-reload: watches code changes, rebuilds, redeploys. Config: `skaffold.yaml`.
+
+```bash
+make k3d/start KIND_CLUSTER_NAME=kuma-1
+export KUBECONFIG=~/.kube/kind-kuma-1-config
+make dev/fetch-demo
+skaffold dev
+```
+
+`skaffold debug` exposes a dlv port (logged on startup) for remote debugging from GoLand/VS Code.
+
+## Envoy admin API
+
+Access via the sidecar container on port 9901:
+
+```bash
+# Full config dump
+kubectl exec deploy/<name> -c kuma-sidecar -- wget -qO- localhost:9901/config_dump
+
+# Filter by section (replace <Section> with Listeners, ClustersConfigDump, Routes, etc.)
+kubectl exec deploy/<name> -c kuma-sidecar -- \
+  wget -qO- localhost:9901/config_dump | \
+  jq '.configs[] | select(."@type" | contains("<Section>"))'
+```
+
+Other endpoints: `/stats` (Envoy metrics), `/clusters` (upstream info), `/server_info` (version).
+
+## Control plane
+
+```bash
+kubectl logs -n kuma-system deploy/kuma-control-plane -f
+kubectl exec -n kuma-system deploy/kuma-control-plane -- \
+  wget -qO- localhost:5681/meshes/default/dataplanes
+```
+
+The CP REST API runs on port 5681. See `pkg/api-server/` for available endpoints.
+
+## Common tasks
+
+### Enable unified resource naming
+
+Requires both helm value AND mesh patch:
+
+```bash
+# Set during deploy via K3D_HELM_DEPLOY_ADDITIONAL_SETTINGS, then:
+kubectl patch mesh default --type merge \
+  -p '{"spec":{"meshServices":{"mode":"Exclusive"}}}'
+```
+
+### Test a policy change locally
+
+1. Build, load, deploy: `make k3d/deploy/helm KIND_CLUSTER_NAME=kuma-1`
+2. Create a test namespace with sidecar injection: `kubectl label namespace <ns> kuma.io/sidecar-injection=enabled`
+3. Deploy a test workload and apply the policy
+4. Inspect Envoy config to verify xDS changes (see Envoy admin API above)
+5. Clean up: `make k3d/stop KIND_CLUSTER_NAME=kuma-1`
+
+## CPU limit workaround
+
+k3d init containers sometimes get throttled on local machines. Set `K3D_HELM_DEPLOY_NO_CNI=true` to reduce resource pressure. If still slow, comment out CPU limits in `pkg/plugins/runtime/k8s/webhooks/injector/injector.go` (search for `NewScaledQuantity(100, kube_api.Milli)`). Revert before committing.
+
+## Test output
+
+Filter noisy macOS linker warnings: `| grep -vE 'LC_DYSYMTAB|#'`
diff --git a/.claude/rules/linting.md b/.claude/rules/linting.md
@@ -0,0 +1,37 @@
+# Linting rules and import conventions
+
+## Required import aliases
+
+The `importas` linter enforces these aliases. Using wrong names fails `make check`:
+
+- `core_mesh` → `github.com/kumahq/kuma/v2/pkg/core/resources/apis/mesh`
+- `mesh_proto` → `github.com/kumahq/kuma/v2/api/mesh/v1alpha1`
+- `system_proto` → `github.com/kumahq/kuma/v2/api/system/v1alpha1`
+- `util_proto` → `github.com/kumahq/kuma/v2/pkg/util/proto`
+- `util_rsa` → `github.com/kumahq/kuma/v2/pkg/util/rsa`
+- `kuma_cmd` → `github.com/kumahq/kuma/v2/pkg/cmd`
+- `bootstrap_k8s` → `github.com/kumahq/kuma/v2/pkg/plugins/bootstrap/k8s`
+- `config_core` → `github.com/kumahq/kuma/v2/pkg/config/core`
+- `core_model` → `github.com/kumahq/kuma/v2/pkg/core/resources/model`
+- `common_api` → `github.com/kumahq/kuma/v2/api/common/v1alpha1`
+- `api_types` → `github.com/kumahq/kuma/v2/api/openapi/types`
+
+## Import ordering
+
+Enforced by `gci`: standard library → third-party → `github.com/kumahq/kuma/v2`
+
+## Forbidden patterns
+
+Use `tracing.SafeSpanEnd(span)` instead of `span.End()`. The `forbidigo` linter blocks direct `span.End()` calls to prevent panics during OTel init/shutdown.
+
+## Blocked packages (depguard)
+
+- `github.com/golang/protobuf` → use `google.golang.org/protobuf` (except for JSON, see next line)
+- `google.golang.org/protobuf/encoding/protojson` → use `github.com/golang/protobuf/jsonpb` (compatibility issues)
+- `sigs.k8s.io/controller-runtime/pkg/log` → use `sigs.k8s.io/controller-runtime` (data race in init containers, see #13299)
+- `io/ioutil` → use `io` and `os`
+- `github.com/kumahq/kuma/v2/app` from `pkg/`. Architectural boundary (`pkg/` cannot import `app/`)
+
+## RBAC validation
+
+`make check` runs `check/rbac`: if any RBAC manifests in `deployments/` change (Role, RoleBinding, ClusterRole, ClusterRoleBinding), `UPGRADE.md` must also be updated.
diff --git a/.claude/rules/policies.md b/.claude/rules/policies.md
@@ -0,0 +1,59 @@
+# Policy plugin system
+
+Policies live in `pkg/plugins/policies/` (MeshTrafficPermission, MeshHTTPRoute, MeshTimeout, etc.).
+
+## Directory structure per policy
+
+```
+{policyname}/
+├── api/v1alpha1/
+│   ├── {policyname}.go              # HAND-WRITTEN: spec struct with +kuma:policy markers
+│   ├── validator.go                 # HAND-WRITTEN: validation logic
+│   ├── deprecated.go                # HAND-WRITTEN: deprecation warnings (optional)
+│   ├── zz_generated.resource.go     # GENERATED
+│   ├── zz_generated.deepcopy.go     # GENERATED
+│   ├── zz_generated.helpers.go      # GENERATED
+│   └── rest.yaml                    # GENERATED: OpenAPI spec
+├── k8s/v1alpha1/
+│   ├── groupversion_info.go         # HAND-WRITTEN: K8s group/version
+│   ├── zz_generated.deepcopy.go     # GENERATED
+│   └── zz_generated.types.go        # GENERATED
+├── plugin/v1alpha1/
+│   ├── plugin.go                    # HAND-WRITTEN: xDS generation logic
+│   ├── plugin_test.go               # HAND-WRITTEN: tests with testdata/
+│   └── testdata/                    # Golden files
+└── zz_generated.plugin.go           # GENERATED: plugin registration
+```
+
+**Rule**: only edit hand-written files. Never edit `zz_generated.*` or `rest.yaml`.
+
+## After changing a policy
+
+```bash
+make generate    # Regenerate all dependent files
+make check       # Lint and validate
+make test TEST_PKG_LIST=./pkg/plugins/policies/{policyname}/...
+```
+
+## Policy spec markers
+
+Add above the main struct in `api/v1alpha1/{policyname}.go`:
+- `// +kuma:policy:singular_display_name=...`: UI name
+- `// +kuma:policy:skip_registration=true`: test-only policies
+- `// +kuma:policy:scope=Mesh`: Mesh or Global scope
+
+Field markers: `+kuma:discriminator` (union types), `+kuma:non-mergeable-struct`
+
+## Plugin interface
+
+Policies implement `core_plugins.PolicyPlugin`:
+- `MatchedPolicies()`: finds policies applying to a dataplane (use `matchers.MatchedPolicies()`)
+- `Apply()`: modifies Envoy xDS `ResourceSet` based on matched policies
+
+Access matched policies in Apply: `proxy.Policies.Dynamic[api.PolicyType]`
+
+## Generation pipeline
+
+`make generate` runs per policy: `policy-gen core-resource` → `k8s-resource` → `plugin-file` → `helpers` → `openapi`
+
+**Gotcha**: `tools/resource-gen` depends on `tools/policy-gen`, so modifying policy-gen forces resource-gen rebuild.
diff --git a/.claude/rules/release.md b/.claude/rules/release.md
@@ -0,0 +1,28 @@
+# Release process
+
+## Branch/tag format
+
+- Branch: `release-X.Y`
+- Tag: `vX.Y.Z` (WITH `v` prefix)
+- Default base: `master`
+- Latest versions: see `versions.yml`
+
+## Steps
+
+1. Verify CI green on `release-X.Y`
+2. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"` then `git push --no-verify upstream vX.Y.Z`
+3. Monitor build-test-distribute workflow
+4. Smoke tests (Universal + K8s)
+5. `gh workflow run release.yaml --repo kumahq/kuma --ref master -f version=X.Y.Z -f check=true`
+6. Publish release notes
+7. Kong Mesh sync (PRs, tag, build, release)
+8. Post-release: docs metadata, merge changelog/docs PRs
+9. Verify: `curl -L https://kuma.io/installer.sh | VERSION=vX.Y.Z sh -`
+10. Announce (GTM Jira, notify EM/PM on #team-mesh)
+
+## Utilities
+
+- Check dep version: `git show upstream/<branch>:go.mod | grep <dep>`
+- Image scan: `trivy image <image>:<tag>`
+- Go dep scan: `osv-scanner --lockfile=go.mod`
+- Update deps: `gh workflow run update-insecure-dependencies.yaml --repo kumahq/kuma` (runs daily 03:00 UTC)
diff --git a/.claude/rules/testing.md b/.claude/rules/testing.md
@@ -0,0 +1,63 @@
+# Testing patterns
+
+## Suite structure
+
+Each package has `*_suite_test.go` with:
+```go
+func TestXxx(t *testing.T) { test.RunSpecs(t, "Suite Name") }
+```
+For E2E tests, use `test.RunE2ESpecs()` instead (sets higher Gomega timeouts).
+
+## Imports
+
+Use dot imports for Ginkgo/Gomega:
+```go
+. "github.com/onsi/ginkgo/v2"
+. "github.com/onsi/gomega"
+```
+
+## Golden file matchers
+
+- `matchers.MatchGoldenYAML("testdata", "file.yaml")`: YAML comparison
+- `matchers.MatchGoldenJSON("testdata", "file.json")`: JSON comparison
+- `matchers.MatchGoldenEqual("testdata", "file.txt")`: raw string equality
+- `matchers.MatchGoldenXML("testdata", "file.xml")`: XML comparison
+- `matchers.MatchProto()`: protobuf message comparison with detailed diffs
+
+Update all golden files: `UPDATE_GOLDEN_FILES=true make test`
+
+## Table-driven tests
+
+Use `DescribeTable`/`Entry` for parameterized tests:
+```go
+DescribeTable("description",
+    func(input, expected string) { ... },
+    Entry("case 1", "input1", "expected1"),
+)
+```
+
+Auto-load from testdata: `test.EntriesForFolder("testdata/folder")` scans for `.input.yaml` files.
+
+## Test resource builders
+
+Fluent API in `pkg/test/resources/builders/`:
+```go
+builders.Dataplane().WithName("dp-1").WithMesh("default").WithAddress("127.0.0.1").Build()
+```
+Pre-built samples in `pkg/test/resources/samples/`.
+
+## Mocks
+
+Hand-written stubs only, no mockgen or counterfeiter. Implement the minimal interface in the test file itself.
+
+## Async testing
+
+- `test.Within(timeout, func() { ... })`: wraps async task with timeout and GinkgoRecover
+- `Eventually()` / `Consistently()` for async Gomega assertions
+- Spawn goroutines with `defer GinkgoRecover()` for panic safety
+
+## Test ordering
+
+- `Ordered` modifier on `Describe()` for sequential test execution
+- `Serial` for individual serial tests
+- Default: parallel execution within suites
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,136 @@
+# CLAUDE.md
+
+Kuma - CNCF service mesh (Envoy-based) for K8s/VMs. L4-L7 connectivity, security, observability, multi-zone/multi-mesh.
+
+## Commands
+
+```bash
+make install              # Install dev tools (runs: mise install + buf dep update)
+make build                # Build all components
+make format               # Format and generate code (auto-fix)
+make check                # Run format + lint, then verify no files changed
+make generate             # Generate code (protobuf, policies, resources)
+make test                 # Run tests
+make test/e2e             # Run E2E tests (slow, requires cluster setup)
+
+make build/kuma-cp        # Build control plane
+make build/kuma-dp        # Build data plane
+make build/kumactl        # Build CLI
+
+make test TEST_PKG_LIST=./pkg/xds/...    # Test specific package
+UPDATE_GOLDEN_FILES=true make test       # Update golden files
+make k3d/start && skaffold dev           # Dev environment
+```
+
+## Workflow
+
+**Code quality principles** (CRITICAL):
+
+1. **Minimal, surgical changes only**
+   - Modify ONLY what's necessary; keep PRs small (<10 files)
+   - Don't refactor unrelated code "while you're there"
+
+2. **Follow existing patterns**
+   - Study surrounding code before making changes
+   - Match naming conventions, error handling, structure
+   - When in doubt, ask for clarification
+
+3. **No bloated changes**
+   - No unnecessary abstractions or `utils.go`/`helpers.go` files
+   - No new dependencies without explicit discussion
+   - Remove unused code you encounter, but don't hunt for it
+
+4. **Quality gates** (code changes only, skip for docs/config/CI)
+   - `make format` to auto-fix, then `make check` to validate (fails if files changed)
+   - Fix ALL linting issues (config: `.golangci.yml`, see `.claude/rules/linting.md`)
+   - `git diff` to verify changes are focused
+
+### Standard workflow
+
+1. `make check` to ensure clean starting state
+2. Read existing code in relevant `pkg/` directory
+3. Write tests first (`*_test.go`, Ginkgo/Gomega)
+4. Implement minimal, focused changes
+5. `make format && make check && make test` to validate
+
+## Git & PRs
+
+```bash
+git push --no-verify <remote> branch-name    # ALWAYS use --no-verify
+```
+
+- **Commit format**: `type(scope): description`, e.g., `feat(xds):`, `fix(meshtrace):`, `chore(deps):`
+- **Commit signing**: use `git commit -s` (DCO `Signed-off-by:` required by CI)
+- **Active branches**: see `active-branches.json`
+- **Base branch**: `master`
+- **PR template**: `.github/PULL_REQUEST_TEMPLATE.md`
+- **Changelog**: from PR title or `> Changelog: {<desc>,skip}`
+- **CI labels**: MUST use `gh pr create --label "ci/..."`. Labels added after creation are ignored by CI
+- **MADR**: `docs/madr/decisions/000-template.md` for features/architecture decisions
+- **Downstream refs**: say "downstream project" or "enterprise fork". Never mention Kong Mesh in PRs/commits (private repo)
+
+## Architecture
+
+### Components
+
+- `kuma-cp`: control plane, serves xDS configs to data planes, manages mTLS certs, coordinates zones
+- `kuma-dp`: data plane proxy (wraps Envoy), connects to `kuma-cp` for bootstrap config
+- `kumactl`: CLI for `kuma-cp` REST API
+- `kuma-cni`: CNI plugin for transparent proxy setup on K8s
+
+### Key directories
+
+- `pkg/core/`: core resource types and managers
+- `pkg/xds/`: Envoy xDS config generation (listeners, clusters, routes, endpoints)
+- `pkg/kds/`: Kuma Discovery Service, syncs resources between Global CP and Zone CPs
+- `pkg/api-server/`: REST API server (validate external inputs here)
+- `pkg/dp-server/`: data plane server (SDS, health checks)
+- `pkg/plugins/policies/`: policy plugins; see `.claude/rules/policies.md`
+- `pkg/plugins/`: plugin architecture (bootstrap, runtime, CA, resources, policies)
+- `pkg/transparentproxy/`: transparent proxy (iptables, eBPF)
+- `pkg/config/`: configuration management
+- `pkg/test/`: test utilities, matchers, and resource builders
+- `tools/`: code generation tools (policy-gen, resource-gen, openapi)
+
+### Multi-zone
+
+- Global CP coordinates Zone CPs via KDS (`pkg/kds/`)
+- Zone Ingress/Egress handle cross-zone traffic
+- Supports Kubernetes and Universal (VM/bare metal)
+
+### Code generation
+
+Run `make generate` after changes to `.proto` files, `pkg/plugins/policies/*/api/` dirs, or resource definitions. Generated files: `zz_generated.*`, `*.pb.go`, `*.pb.validate.go`, `rest.yaml`
+
+### Tool management
+
+Uses `mise` (config: `mise.toml`). Install via `make install`. Includes: buf, ginkgo, helm, kind, kubectl, protoc, golangci-lint, skaffold.
+
+## Testing
+
+- **Framework**: Ginkgo (BDD) + Gomega assertions (`*_test.go`); see `.claude/rules/testing.md`
+- **Golden matchers**: `MatchGoldenYAML`, `MatchGoldenJSON`, `MatchGoldenEqual`, `MatchProto`
+- **Golden files**: in `testdata/` dirs. Update with `UPDATE_GOLDEN_FILES=true make test`
+- **Mocks**: hand-written stubs (no mockgen/counterfeiter). Implement the interface in the test file
+- **E2E**: `make test/e2e`. Slow, requires cluster setup
+
+## Gotchas
+
+- **RBAC gate**: if `deployments/` RBAC manifests change, `UPGRADE.md` must also be updated or `make check` fails
+- **Import aliases required**: `.golangci.yml` enforces `core_mesh`, `mesh_proto`, `core_model`, `common_api`, etc. See `.claude/rules/linting.md`
+- **Cached resources are read-only**: `pkg/core/resources/manager/cache.go` returns shared instances. Never modify them
+- **`pkg/` cannot import `app/`**: architectural boundary enforced by depguard linter
+
+## Common issues
+
+- Missing dependencies → `make install`
+- Outdated generated code → `make generate`
+- Formatting errors → `make format` (auto-fixes), then `make check` (validates)
+- Golden file mismatches → `UPDATE_GOLDEN_FILES=true make test`
+
+## Notes
+
+- Versions: `active-branches.json` and `versions.yml` in the repo root
+- Docs: `DEVELOPER.md` (setup), `CONTRIBUTING.md` (PR workflow)
+- Release process: see `.claude/rules/release.md`
+- Local dev and debugging: see `.claude/rules/debug.md`
PATCH

echo "Gold patch applied."
