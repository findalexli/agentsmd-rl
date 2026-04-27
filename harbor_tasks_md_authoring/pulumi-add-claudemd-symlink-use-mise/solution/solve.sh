#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pulumi

# Idempotency guard
if grep -qF "This repo uses [mise](https://mise.jdx.dev/) to manage tool versions (Go, Node, " "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "- Anything that adds or changes the engine, resource options, or the provider in" "pkg/AGENTS.md" && grep -qF "All commands run from `sdk/go/`. Prefix with `mise exec --` if mise is not activ" "sdk/go/AGENTS.md" && grep -qF "- You must run `mise exec -- make install` to make the SDK available via `yarn l" "sdk/nodejs/AGENTS.md" && grep -qF "All commands run from `sdk/python/`. Prefix with `mise exec --` if mise is not a" "sdk/python/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,9 +1,11 @@
 # Agent Instructions
 
 ## What this repo is
+
 The core Pulumi SDK and CLI. Go monorepo with multiple Go modules (`pkg/`, `sdk/`, `tests/`, etc.) and language-specific SDKs (`sdk/nodejs/`, `sdk/python/`, `sdk/go/`, `sdk/pcl/`). Builds the `pulumi` CLI binary and language host binaries.
 
 ## Repo structure
+
 - `pkg/` — Core engine: CLI commands, deployment engine, codegen, resource management, backends
 - `sdk/` — Language SDKs and shared Go SDK code (`sdk/go/`, `sdk/nodejs/`, `sdk/python/`, `sdk/pcl/`)
 - `tests/` — Integration and acceptance tests
@@ -13,68 +15,71 @@ The core Pulumi SDK and CLI. Go monorepo with multiple Go modules (`pkg/`, `sdk/
 - `scripts/` — CI and development helper scripts
 - `changelog/` — Pending changelog entries
 
+## Tool setup
+
+This repo uses [mise](https://mise.jdx.dev/) to manage tool versions (Go, Node, Python, protoc, etc.). See `.mise.toml` for the full list. If mise is installed and activated (via `mise activate` in your shell profile), tool versions are handled automatically and you can run `make` directly. Otherwise, **prefix all `make` commands with `mise exec --`** to ensure the correct tool versions are used:
+
+```sh
+mise exec -- make build
+mise exec -- make lint
+```
+
 ## Command canon
+
 All commands assume you're at the repo root.
 
-- **Build CLI and SDKs:** `make build` (builds `bin/pulumi`, proto, WASM display, and language SDKs)
-- **Build CLI and certain SDKs:** `SDKS=nodejs python" make build` (builds `bin/pulumi`, proto, WASM display, nodejs and python SDKs)
-- **Build a single SDK:** `cd sdk/nodejs && make build` (or `sdk/python`, `sdk/go`, `sdk/pcl`)
-- **Lint:** `make lint` (runs golangci-lint across all Go modules + validates pulumi.json schema)
-- **Lint fix:** `make lint_fix`
-- **Format Code:** `make format` (runs gofumpt and formatting for python and nodejs)
-- **Fast tests:** `make test_fast` (unit tests, uses `-short` flag)
-- **Full tests:** `make test_all` (unit + integration tests)
-- **Language conformance tests:** `./scripts/run-conformance.sh` (runs language conformance tests against language SDKs, exercises codegen and runtime)
+- **Build CLI and SDKs:** `mise exec -- make build`
+- **Build CLI with specific SDKs:** `SDKS="nodejs python" mise exec -- make build`
+- **Build a single SDK:** `cd sdk/nodejs && mise exec -- make build` (or `sdk/python`, `sdk/go`, `sdk/pcl`)
+- **Lint:** `mise exec -- make lint`
+- **Lint fix:** `mise exec -- make lint_fix`
+- **Format:** `mise exec -- make format`
+- **Fast tests:** `mise exec -- make test_fast`
+- **Full tests:** `mise exec -- make test_all`
+- **Language conformance tests:** `./scripts/run-conformance.sh`
 - **Test a single Go package:** `cd pkg && go test -count=1 -tags all ./codegen/go/...`
-- **Tidy check:** `make tidy` (verifies `go mod tidy` is clean)
-- **Tidy fix:** `make tidy_fix` (verifies `go mod tidy` is clean and repairs errors if it is not)
-- **Proto generation:** `make build_proto` (regenerates from `proto/*.proto`)
-- **Proto check:** `make check_proto` (fails if proto output is stale)
-- **Changelog entry:** `make changelog` (interactive — creates a file in `changelog/`)
-- **Go workspace:** `make work` (creates `go.work` for cross-module development)
-
-### Per-SDK test commands
-- `cd sdk/nodejs && make test_fast`
-- `cd sdk/python && make test_fast`
-- `cd sdk/go && make test_fast`
+- **Tidy check:** `mise exec -- make tidy`
+- **Tidy fix:** `mise exec -- make tidy_fix`
+- **Proto generation:** `mise exec -- make build_proto`
+- **Proto check:** `mise exec -- make check_proto`
+- **Changelog entry:** `mise exec -- make changelog` (interactive)
+- **Go workspace:** `mise exec -- make work`
 
 ## Key invariants
-- The repo has multiple Go modules (`pkg/go.mod`, `sdk/go.mod`, `tests/go.mod`, etc.). Changes to `go.mod` in one module may require updates in others. Run `make tidy` to verify.
-    - Use `make work` to create a `go.work` file for cross-module development with proper replace directives.
-- Proto-generated files in `sdk/proto/go/`, `sdk/nodejs/proto/`, `sdk/python/lib/pulumi/runtime/proto/` must stay in sync with `proto/*.proto`. CI enforces this via `make check_proto`.
+
+- Multiple Go modules (`pkg/go.mod`, `sdk/go.mod`, `tests/go.mod`, etc.). Changes to `go.mod` in one module may require updates in others. Run `mise exec -- make tidy` to verify.
+  - Use `mise exec -- make work` to create a `go.work` file for cross-module development.
+- Proto-generated files must stay in sync with `proto/*.proto`. CI enforces via `mise exec -- make check_proto`.
 - `pkg/codegen/schema/pulumi.json` is the metaschema. It must be valid JSON Schema and pass biome formatting.
-- Changelog entries are required for most PRs. Run `make changelog` to create one.
+- Changelog entries are required for most PRs. Run `mise exec -- make changelog` to create one.
 - PRs are squash-merged — the PR description becomes the commit message.
-- Integration tests need the CLI and SDKs to be built prior to running.
-    - For the nodejs SDK, you must run `make install` to ensure thatr the SDK is available to `yarn link`.
-    - `bin/` must be on the `PATH` when running integration tests, as that directory contains the built CLI and language hosts
+- Integration tests need the CLI and SDKs built first. `bin/` must be on `PATH`.
 
 ## Forbidden actions
+
 - Do not run `git push --force`, `git reset --hard`, or `rm -rf` without explicit approval.
 - Do not skip linting.
-- Do not edit generated proto files by hand — edit `proto/*.proto` and run `make build_proto`.
-- Do not edit other generated files by hand. Some tests use golden files that are generated or updated by running the tests with `PULUMI_ACCEPT=1`.
+- Do not edit generated proto files by hand — edit `proto/*.proto` and run `mise exec -- make build_proto`.
+- Do not edit other generated files by hand. Some tests use golden files updated with `PULUMI_ACCEPT=1`.
 - Do not add external runtime dependencies without discussion.
 - Do not fabricate test output or changelog entries.
-- Do not edit files in `sdk/proto/go/`, `sdk/nodejs/proto/`, or `sdk/python/lib/pulumi/runtime/proto/` directly.
 - Do not make sweeping changes, refactor unrelated code, or add unnecessary abstractions.
 
 ## Escalate immediately if
-- A change touches the public SDK surface (`sdk/go/...`, `sdk/nodejs/...`, `sdk/python/...` exported types/functions).
-- A change touches the public interface of the `pulumi` SDK (`pkg/cmd/pulumi/...`, built using `github.com/spf13/cobra`).
+
+- A change touches the public SDK surface (exported types/functions in `sdk/go/`, `sdk/nodejs/`, `sdk/python/`).
+- A change touches the public CLI interface (`pkg/cmd/pulumi/`, built with `github.com/spf13/cobra`).
 - Requirements are ambiguous or conflicting.
 - Tests fail after two debugging attempts.
 - A change affects the deployment engine's state serialization or resource lifecycle.
 - A change affects the events emitted by the engine.
 - A change requires modifying protobuf definitions.
 
 ## If you change...
-- Any `.go` file → `make format && make lint && make test_fast`
-- `proto/*.proto` → `make build_proto && make check_proto` and commit generated files
-- `go.mod` or `go.sum` in any module → run `make tidy` (runs `./scripts/tidy.sh --check`)
-- `pkg/codegen/schema/pulumi.json` → `make lint_pulumi_json`
-- `sdk/nodejs/` TypeScript files → `cd sdk/nodejs && make lint && make test_fast`
-- `sdk/python/` Python files → `cd sdk/python && make lint && make test_fast`
-- Anything in `pkg/codegen/` → run codegen tests: `cd pkg && go test -count=1 -tags all ./codegen/...`
-- Anything in `pkg/backend/display/...` → add a test that uses pre-constructed, JSON-serialized engine events (ref. testProgressEvents)
-- Anything that adds or changes the engine, resource options, or the provider interface → add a test to `pkg/engine/lifecycletest/`
+
+- Any `.go` file → `mise exec -- make format && mise exec -- make lint && mise exec -- make test_fast`
+- `proto/*.proto` → `mise exec -- make build_proto && mise exec -- make check_proto` and commit generated files
+- `go.mod` or `go.sum` in any module → `mise exec -- make tidy`
+- `pkg/codegen/schema/pulumi.json` → `mise exec -- make lint_pulumi_json`
+
+See subdirectory `AGENTS.md` files (`pkg/`, `sdk/nodejs/`, `sdk/python/`, `sdk/go/`) for package-specific instructions.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/pkg/AGENTS.md b/pkg/AGENTS.md
@@ -0,0 +1,14 @@
+# Core Engine (`pkg/`)
+
+## Testing
+
+- **Unit tests:** `cd pkg && go test -count=1 -tags all ./...`
+- **Codegen tests:** `cd pkg && go test -count=1 -tags all ./codegen/...`
+- **Codegen for a specific language:** `cd pkg && go test -count=1 -tags all ./codegen/go/...`
+- **Lifecycle tests:** `cd pkg && go test -count=1 -tags all ./engine/lifecycletest/...`
+
+## If you change...
+
+- Anything in `pkg/codegen/` → run codegen tests: `cd pkg && go test -count=1 -tags all ./codegen/...`
+- Anything in `pkg/backend/display/` → add a test using pre-constructed, JSON-serialized engine events (ref. `testProgressEvents`)
+- Anything that adds or changes the engine, resource options, or the provider interface → add a test to `pkg/engine/lifecycletest/`
diff --git a/sdk/go/AGENTS.md b/sdk/go/AGENTS.md
@@ -0,0 +1,14 @@
+# Go SDK (`sdk/go/`)
+
+## Commands
+
+All commands run from `sdk/go/`. Prefix with `mise exec --` if mise is not activated.
+
+- **Build:** `mise exec -- make build`
+- **Lint:** `mise exec -- make lint`
+- **Fast tests:** `mise exec -- make test_fast`
+- **Full tests:** `mise exec -- make test_all`
+
+## If you change...
+
+- Go files → `mise exec -- make lint && mise exec -- make test_fast`
diff --git a/sdk/nodejs/AGENTS.md b/sdk/nodejs/AGENTS.md
@@ -0,0 +1,17 @@
+# Node.js SDK (`sdk/nodejs/`)
+
+## Commands
+
+All commands run from `sdk/nodejs/`. Prefix with `mise exec --` if mise is not activated.
+
+- **Build:** `mise exec -- make build`
+- **Install (required before integration tests):** `mise exec -- make install`
+- **Lint:** `mise exec -- make lint`
+- **Lint fix:** `mise exec -- make lint_fix`
+- **Fast tests:** `mise exec -- make test_fast`
+- **Full tests:** `mise exec -- make test_all`
+
+## If you change...
+
+- TypeScript files → `mise exec -- make lint && mise exec -- make test_fast`
+- You must run `mise exec -- make install` to make the SDK available via `yarn link` before running integration tests.
diff --git a/sdk/python/AGENTS.md b/sdk/python/AGENTS.md
@@ -0,0 +1,16 @@
+# Python SDK (`sdk/python/`)
+
+## Commands
+
+All commands run from `sdk/python/`. Prefix with `mise exec --` if mise is not activated.
+
+- **Build:** `mise exec -- make build`
+- **Lint:** `mise exec -- make lint`
+- **Lint fix:** `mise exec -- make lint_fix`
+- **Format:** `mise exec -- make format`
+- **Fast tests:** `mise exec -- make test_fast`
+- **Full tests:** `mise exec -- make test_all`
+
+## If you change...
+
+- Python files → `mise exec -- make lint && mise exec -- make test_fast`
PATCH

echo "Gold patch applied."
