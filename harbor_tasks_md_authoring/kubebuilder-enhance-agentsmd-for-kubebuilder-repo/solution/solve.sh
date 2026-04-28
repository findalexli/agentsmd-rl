#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kubebuilder

# Idempotency guard
if grep -qF "**Note:** Boilerplate/template files are Go files that define scaffolding templa" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -18,44 +18,94 @@ It provides scaffolding and abstractions that accelerate the development of **co
 
 ```
 pkg/
-  cli/          CLI commands (init, create api, create webhook, edit, alpha)
-  machinery/    Scaffolding engine (templates, markers, injectors, filesystem)
-  model/        Resource and stage models
-  plugin/       Plugin interfaces and utilities
-  plugins/      Plugin implementations
-    golang/v4/           Main Go operator scaffolding (used by default combined with kustomize/v2; see PluginBundle in cli/init.go)
-    golang/deployimage/  Implements create api interface to generate code to deploy and manage container images with controller
-    common/kustomize/v2/ Kustomize manifests (used by default combined with go/v4; see PluginBundle in cli/init.go)
-    optional/helm/       Helm chart generation to distribute the projects (v1alpha; deprecated, v2alpha)
-    optional/grafana/    Grafana dashboards
-    optional/autoupdate/ Auto-update workflow
-    external/            External plugin support
-docs/book/      mdBook sources + tutorial samples
+  cli/              CLI command implementations
+    alpha/          Alpha/experimental commands (generate, update, etc.)
+    init.go         'init' command + default PluginBundle definition
+    api.go          'create api' command
+    webhook.go      'create webhook' command
+    edit.go         'edit' command
+    root.go         Root command setup
+  machinery/        Scaffolding engine (templates, markers, injectors)
+    template.go     Base template interface
+    inserter.go     Code injection engine
+    marker.go       Marker detection and processing
+    filesystem.go   Filesystem abstraction (uses afero)
+  model/
+    resource/       Resource model (GVK, API, Controller, Webhook)
+    stage/          Plugin execution stages
+  plugin/           Plugin interfaces and utilities
+    interface.go    Core plugin interfaces (Plugin, Init, CreateAPI, etc.)
+    bundle.go       Plugin composition
+    util/           Helper functions for plugin authors
+  plugins/          Plugin implementations (ADD NEW PLUGINS HERE)
+    golang/v4/      Main Go scaffolding (default for go projects)
+      scaffolds/    Scaffolding for init, api, webhook
+        internal/templates/  Template implementations
+    golang/deployimage/  Deploy-image pattern plugin
+    common/kustomize/v2/  Kustomize manifest generation (default)
+    optional/       Optional plugins (enabled via --plugins flag)
+      helm/         Helm chart generation (v1alpha deprecated, v2alpha current)
+      grafana/      Grafana dashboard generation
+      autoupdate/   Auto-update GitHub workflow
+    external/       External plugin support (exec-based plugins)
+docs/book/          mdBook documentation (https://book.kubebuilder.io)
+  src/              Markdown source files
+    **/testdata/    Sample projects used in docs (regenerated)
 test/
-  e2e/          End-to-end tests requiring Kubernetes cluster (v4, helm, deployimage)
-  testdata/     Testdata generation scripts
-testdata/       Generated sample projects (DO NOT EDIT)
-hack/docs/      Documentation generation scripts
+  e2e/              E2E tests requiring Kubernetes cluster
+    v4/             Tests for v4 plugin
+    helm/           Tests for Helm plugin
+    deployimage/    Tests for deploy-image plugin
+    utils/          Test helpers (TestContext, etc.)
+  testdata/         Scripts to generate testdata projects
+    generate.sh     Main generation script
+    test.sh         Tests all testdata projects
+testdata/           Generated complete sample projects (DO NOT EDIT)
+  project-v4/                    Basic v4 project
+  project-v4-multigroup/         Multigroup project
+  project-v4-with-plugins/       Project with optional plugins
+hack/docs/          Documentation generation
+  generate.sh       Regenerate docs samples + marker docs
+  generate_samples.go  Sample generation logic
+cmd/                CLI entry point
+  version.go        Version info (updated by make update-k8s-version)
+main.go             Application entry point
 ```
 
+**Key Locations for Common Tasks:**
+- Add new plugin → `pkg/plugins/<category>/<name>/`
+- Add new template → `pkg/plugins/<plugin>/scaffolds/internal/templates/`
+- Modify CLI commands → `pkg/cli/`
+- Add scaffolding machinery → `pkg/machinery/`
+- Add tests → `test/e2e/<plugin>/` or `pkg/<package>/*_test.go`
+
 ## Critical Rules
 
-### NEVER Manually Edit
+### Do Not Manually Edit Generated Files
 - `testdata/` - regenerated via `make generate-testdata`
 - `docs/book/**/testdata/` - regenerated via `make generate-docs`
 - `*/dist/chart/` - regenerated via `make generate-charts`
 
-### Always Run Before PR
+### File-Specific Requirements
+
+After making changes, run the appropriate commands based on what you modified:
+
+**Generate Commands (rebuild artifacts):**
+- **If you modify files in `hack/docs/internal/`** → run `make install && make generate-docs`
+- **If you modify files in `pkg/plugins/optional/helm/`** → run `make install && make generate-charts`
+- **If you modify any boilerplate/template files** → run `make install && make generate`
+
+**Formatting Commands:**
+- After editing `*.go` → `make lint-fix`
+- After editing `*.md` → `make remove-spaces`
+
+**Always Run Before PR:**
 ```bash
-make generate    # Regenerate all (testdata + docs + k8s version + tidy)
 make lint-fix    # Auto-fix Go code style
 make test-unit   # Verify unit tests pass
 ```
 
-### File-Specific Requirements
-- After editing `*.go` → `make lint-fix`
-- After editing `*.md` → `make remove-spaces`
-- After modifying scaffolding/templates → `make generate`
+**Note:** Boilerplate/template files are Go files that define scaffolding templates, typically located in `pkg/plugins/**/scaffolds/internal/templates/` or files that generate code/configs for scaffolded projects.
 
 ## Development Workflow
 
@@ -65,14 +115,6 @@ make build    # Build to ./bin/kubebuilder
 make install  # Copy to $(go env GOBIN)
 ```
 
-### Generate Everything
-```bash
-make generate              # Master command (runs all below + tidy + remove-spaces)
-make generate-testdata     # Recreate testdata/project-*
-make generate-docs         # Regenerate docs samples & marker docs
-make generate-charts       # Rebuild Helm charts
-```
-
 ### Lint & Format
 ```bash
 make lint       # Check only (golangci-lint + yamllint)
@@ -121,59 +163,83 @@ make test              # CI aggregate (all of above + license)
 ## Core Concepts
 
 ### Plugin Architecture
+
 Plugins implement interfaces from `pkg/plugin/`:
 - `Plugin` - base interface (Name, Version, SupportedProjectVersions)
-- `Init` - provides `init` subcommand
-- `CreateAPI` - provides `create api` subcommand
-- `CreateWebhook` - provides `create webhook` subcommand
-- `Edit` - provides `edit` subcommand
+- `Init` - project initialization (`kubebuilder init`)
+- `CreateAPI` - API creation (`kubebuilder create api`)
+- `CreateWebhook` - webhook creation (`kubebuilder create webhook`)
+- `Edit` - post-init modifications (`kubebuilder edit`)
 - `Bundle` - groups multiple plugins
 
+**Plugin Bundles:**
+
+Default bundle (`pkg/cli/init.go`): `go.kubebuilder.io/v4` + `kustomize.common.kubebuilder.io/v2`
+
+Plugins resolve via `pkg/plugin` registry and execute in order.
+
+**External Plugins:**
+
+Executable binaries in `pkg/plugins/external/` that communicate via JSON over stdin/stdout.
+
 ### Scaffolding Machinery
+
 From `pkg/machinery/`:
 - `Template` - file generation via Go templates
 - `Inserter` - code injection at markers
 - `Marker` - special comments (e.g., `// +kubebuilder:scaffold:imports`)
 - `Filesystem` - abstraction over afero for testability
 
 ### Scaffolded Project Structure
-`kubebuilder init` creates:
+
+Projects generated by the Kubebuilder CLI use the default plugin bundle (`go/v4` + `kustomize/v2`). Each plugin scaffolds different files:
+
+**`go/v4` plugin scaffolds Go code:**
 - `cmd/main.go` - Entry point (manager setup)
-- `api/v1/*_types.go` - API definitions with `+kubebuilder` markers
-- `internal/controller/*_controller.go` - Reconcile logic
-- `config/` - Kustomize manifests (CRDs, RBAC, manager, webhooks)
+- `api/v1/*_types.go` - API definitions with `+kubebuilder` markers (via `create api`)
+- `internal/controller/*_controller.go` - Reconcile logic (via `create api`)
 - `Dockerfile`, `Makefile` - Build and deployment automation
 
+**`kustomize/v2` plugin scaffolds manifests:**
+- `config/` - Kustomize base manifests (CRDs, RBAC, manager, webhooks)
+- `config/crd/` - Custom Resource Definitions (via `create api`)
+- `config/samples/` - Example CR manifests (via `create api`)
+
+**`PROJECT` file:**
+- Project configuration tracking plugins, resources, domain, and layout
+
+**Note:** These are files in projects generated BY Kubebuilder, not the Kubebuilder source code itself.
+
 ### Reconciliation Pattern
+
 Controllers implement `Reconcile(ctx, req) (ctrl.Result, error)`:
+
 - **Idempotent** - Safe to run multiple times
 - **Level-triggered** - React to current state, not events
 - **Requeue on pending work** - Return `ctrl.Result{Requeue: true}`
 
 ### Testing Pattern
-E2E tests use `test/e2e/utils/test_context.go`:
+E2E tests use `utils.TestContext` from `test/e2e/utils/test_context.go`:
+
 ```go
-ctx := utils.NewTestContext("kubebuilder", "GO111MODULE=on")
-ctx.Init()                    // Run kubebuilder init
-ctx.CreateAPI(...)            // Run create api
-ctx.Make("build")             // Run make targets
-ctx.LoadImageToKindCluster()  // Load image to kind
+ctx := utils.NewTestContext(util.KubebuilderBinName, "GO111MODULE=on")
+ctx.Init("--domain", "example.com", "--repo", "example.com/project")
+ctx.CreateAPI("--group", "crew", "--version", "v1", "--kind", "Captain")
+ctx.Make("build", "test")
+ctx.LoadImageToKindCluster()
 ```
 
-## Tool Commands
+## CLI Reference
+
+After `make install`:
 
-### CLI Commands
 ```bash
 kubebuilder init --domain example.com --repo github.com/example/myproject
 kubebuilder create api --group batch --version v1 --kind CronJob
 kubebuilder create webhook --group batch --version v1 --kind CronJob
 kubebuilder edit --plugins=helm/v2-alpha
-```
-
-### Alpha Commands (Experimental)
-```bash
-kubebuilder alpha generate  # Generate from existing PROJECT file
-kubebuilder alpha update    # Update to latest plugin versions
+kubebuilder alpha generate    # Experimental: generate from PROJECT file
+kubebuilder alpha update      # Experimental: update to latest plugin versions
 ```
 
 ## Common Patterns
@@ -191,6 +257,7 @@ kubebuilder alpha update    # Update to latest plugin versions
 - Tests depending on the Kubebuilder binary should use: `utils.NewTestContext(util.KubebuilderBinName, "GO111MODULE=on")`
 
 ### Test Organization
+
 - **Unit tests** (`*_test.go` in `pkg/`) - Test individual packages in isolation, fast
 - **Integration tests** (`*_integration_test.go` in `pkg/`) - Test multiple components together without cluster
   - Must have `//go:build integration` tag at the top
@@ -209,11 +276,12 @@ kubebuilder alpha update    # Update to latest plugin versions
 ## Search Tips
 
 ```bash
-# Use rg (ripgrep) for searching
-rg "pattern" --type go
-rg "\\+kubebuilder:scaffold" --type go  # Find markers to inject code via Machinery
-rg "\\+kubebuilder" --type go  # Find all markers
-rg "type.*Plugin struct" pkg/plugins/   # Find plugins
+rg "\\+kubebuilder:scaffold" --type go  # Find markers
+rg "type.*Plugin struct" pkg/plugins/   # Plugin implementations
+rg "PluginBundle" pkg/cli/              # Plugin registration
+rg "func.*SetTemplateDefaults"          # Template definitions
+rg "func new.*Command" pkg/cli/         # CLI commands
+rg "NewTestContext" test/e2e/           # E2E test setup
 ```
 
 ## Design Philosophy
@@ -225,8 +293,34 @@ rg "type.*Plugin struct" pkg/plugins/   # Find plugins
 
 ## References
 
-- `Makefile` - All automation targets (source of truth for commands)
-- `CONTRIBUTING.md` - CLA, pre-submit checklist, PR emoji policy
-- `VERSIONING.md` - Release workflow and PR tagging
-- `docs/book/` - User documentation (https://book.kubebuilder.io)
-- `test/e2e/utils/test_context.go` - E2E test helpers
+### Essential Files
+- **`Makefile`** - All automation targets (source of truth for build/test commands)
+- **`CONTRIBUTING.md`** - CLA, pre-submit checklist, PR requirements
+- **`VERSIONING.md`** - Release workflow, versioning policy, PR tagging
+- **`go.mod`** - Go version and dependencies
+
+### Key Directories
+- **`pkg/`** - Core Kubebuilder code (CLI, plugins, machinery)
+- **`test/e2e/`** - End-to-end tests with Kubernetes cluster
+- **`testdata/`** - Generated sample projects (regenerated automatically)
+- **`docs/book/`** - User documentation source (https://book.kubebuilder.io)
+
+### Important Code Files
+- **`pkg/cli/init.go`** - Default plugin bundle definition
+- **`pkg/plugin/interface.go`** - Plugin interface definitions
+- **`pkg/machinery/scaffold.go`** - Scaffolding engine
+- **`test/e2e/utils/test_context.go`** - E2E test helpers
+- **`cmd/version.go`** - Version info (includes K8S version)
+
+### Scripts
+- **`test/testdata/generate.sh`** - Regenerate all testdata projects
+- **`hack/docs/generate.sh`** - Regenerate documentation samples
+- **`test/e2e/local.sh`** - Run e2e tests locally with Kind
+
+### External Resources
+- **Kubebuilder Book**: https://book.kubebuilder.io
+- **Kubebuilder Repo**: https://github.com/kubernetes-sigs/kubebuilder
+- **controller-runtime**: https://github.com/kubernetes-sigs/controller-runtime
+- **controller-tools**: https://github.com/kubernetes-sigs/controller-tools
+- **API Conventions**: https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md
+- **Operator Pattern**: https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
PATCH

echo "Gold patch applied."
