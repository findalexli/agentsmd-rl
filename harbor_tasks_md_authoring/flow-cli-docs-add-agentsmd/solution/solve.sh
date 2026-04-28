#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flow-cli

# Idempotency guard
if grep -qF "- `make generate` \u2014 `go generate ./...`; run before `lint`, `ci`, or any test to" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,106 @@
+# AGENTS.md
+
+Guidance for AI coding agents working in this repo. Every claim below is sourced from the
+Makefile, `go.mod`, `ci.yml`, `CONTRIBUTING.md`, or verified source files — do not add
+unverified commands or paths.
+
+## Overview
+
+`flow-cli` is the official command-line tool for the Flow blockchain: deploy contracts, run
+transactions/scripts, manage accounts/keys, and run a bundled emulator. Go 1.25.1 module
+(`github.com/onflow/flow-cli`), built on [Cobra](https://github.com/spf13/cobra). All
+blockchain logic is delegated to the external `github.com/onflow/flowkit/v2` module. Entry
+point is `cmd/flow/main.go`. License: Apache-2.0.
+
+## Build and Test Commands
+
+CGO is required (BLS crypto). `go build` / `go test` need these env vars set:
+`CGO_ENABLED=1 CGO_CFLAGS="-O2 -D__BLST_PORTABLE__ -std=gnu11"`.
+
+- `make binary` — build `./cmd/flow/flow`; ldflags inject version, commit, and analytics tokens
+- `make test` — `go test -coverprofile=coverage.txt ./...` with CGO flags set
+- `make ci` — `generate test coverage` (this is what GitHub Actions runs)
+- `make coverage` — emits `index.html` and `cover-summary.txt`, only when `COVER=true`
+- `make lint` — `golangci-lint run -v ./...`; depends on `make generate`
+- `make fix-lint` — golangci-lint with `--fix`
+- `make generate` — `go generate ./...`; run before `lint`, `ci`, or any test touching generated code
+- `make check-headers` — `./check-headers.sh`, verifies Apache-2.0 header on every `.go` file
+- `make check-tidy` — `go mod tidy` (CI runs this; fails if `go.mod`/`go.sum` drift)
+- `make clean` — removes binaries under `cmd/flow/`
+- `make versioned-binaries` — cross-compiles linux/darwin/windows × amd64/arm64
+- `make publish` — uploads versioned binaries to `gs://flow-cli` via `gsutil`
+- `make release` — runs `ghcr.io/goreleaser/goreleaser-cross:v1.25.0` in Docker
+- `make test-e2e-emulator` — `flow -f tests/flow.json emulator start`
+- `SKIP_NETWORK_TESTS=1 make test` — skip tests that reach Flow mainnet/testnet (CONTRIBUTING.md)
+- `nix develop` — enter dev shell from `flake.nix`; then `go run cmd/flow/main.go`
+
+## Architecture
+
+Cobra CLI. `cmd/flow/main.go` wires every subcommand into the root `flow` command and defines
+eight command groups (super, resources, interactions, tools, project, security, manager, schedule).
+
+**`internal/command/`** — shared framework. `command.Command` wraps `cobra.Command` with two
+run modes: `Run` (no project state) and `RunS` (requires `*flowkit.State` loaded from
+`flow.json`). `AddToParent()` handles loading `flow.json`, gateway/network resolution,
+`flowkit.Services` init, version check, analytics, and error formatting. Global flags
+(`internal/command/global_flags.go`): `--network`, `--host`, `--log`, `--output`, `--filter`,
+`--save`, `--config-path`, `--yes`, `--skip-version-check`. Every `Result` must implement
+`String()`, `Oneliner()`, and `JSON()`.
+
+**`internal/super/`** — super commands (`flow init`, `flow dev`, `flow generate`, `flow flix`).
+Scaffolding engine under `internal/super/generator/` with `templates/` and `fixtures/`.
+
+**Feature packages** (`internal/<name>/`) — one per top-level command; each exports a
+`Cmd *cobra.Command` (or `Command`) registered in `main.go`:
+`accounts`, `blocks`, `cadence`, `collections`, `config`, `dependencymanager`, `emulator`,
+`events`, `evm`, `keys`, `mcp`, `project`, `quick` (`flow deploy`, `flow run`), `schedule`
+(transaction scheduler: `setup`/`get`/`list`/`cancel`/`parse`), `scripts`, `settings`,
+`signatures`, `snapshot`, `status`, `test`, `tools` (`dev-wallet`, `flowser`), `transactions`,
+`version`. Support: `internal/util/`, `internal/prompt/`.
+
+**`build/build.go`** — version/commit variables injected via `-ldflags` at build time.
+**`common/branding/`** — styling/ASCII constants.
+**`flowkit/`** (top-level) — **historical artifact**; contains only `README.md` and
+`schema.json`. All Go code moved to the external `github.com/onflow/flowkit/v2`.
+**`docs/`** — hand-maintained Markdown reference pages, one per command, published to
+developers.flow.com.
+**`testing/better/`** — shared test helpers.
+
+## Conventions and Gotchas
+
+- **`make generate` before `make lint` and CI workflows.** `lint` declares `generate` as a
+  prerequisite; `ci` runs `generate test coverage` in that order.
+- **CGO is not optional.** Plain `go build ./...` / `go test ./...` without the CGO env vars
+  above will fail on the BLS crypto dependency (`__BLST_PORTABLE__`).
+- **Register new commands via `command.Command.AddToParent(cmd)`** (not raw `cmd.AddCommand`)
+  so shared boilerplate — `flow.json` load, gateway init, error formatting — runs. See
+  `cmd/flow/main.go` for both registration styles.
+- **Command naming is `noun verb`** (`flow accounts get`, not `flow get-accounts`) — see
+  "CLI Guidelines" in `CONTRIBUTING.md`.
+- **Prefer flags over positional args.** Use an arg only for the single primary required value.
+- **`--output json` must always work.** Every `Result` implements `JSON()`; never gate
+  machine-readable output behind a subcommand.
+- **stdout for normal output, stderr for errors.** No stack traces on error; `--log debug`
+  is the escape hatch.
+- **Every `.go` file needs the Apache-2.0 header.** `check-headers.sh` greps for
+  `Licensed under the Apache License` or `Code generated (from|by)` and fails CI otherwise.
+- **goimports `local-prefixes: github.com/onflow/flow-cli`** (`.golangci.yml`) — internal
+  imports group separately from third-party.
+- **Linters enabled:** `errcheck`, `govet`, `ineffassign`, `misspell`, plus `goimports`
+  formatter. CI pins `golangci-lint v2.4.0` (`.github/workflows/ci.yml`).
+- **`SKIP_NETWORK_TESTS=1`** skips tests that reach mainnet/testnet nodes — use in Nix or
+  egress-restricted CI (CONTRIBUTING.md "Skipping Network-Dependent Tests").
+- **`syscall.Exit` in `cmd/flow/main.go` is intentional** — works around a gRPC cleanup
+  regression that appeared in Go 1.23.1 (inline comment in `main.go`).
+- **`version.txt` is deprecated** for CLI versions after v1.18.0 (CONTRIBUTING.md
+  "Releasing"). The semver is derived from the git tag via `-ldflags` into `build.semver`.
+- **Analytics tokens (`MIXPANEL_PROJECT_TOKEN`, `ACCOUNT_TOKEN`) are baked in at build time**
+  via ldflags in the Makefile — rebuild, don't patch the binary.
+
+## Files Not to Modify
+
+- `go.sum` — regenerate via `go mod tidy` / `make check-tidy`, never hand-edit.
+- `flake.lock` — update via `nix flake update`.
+- `flowkit/` top-level directory — legacy stub; real code lives in `github.com/onflow/flowkit/v2`.
+- `version.txt` — deprecated post v1.18.0; leave it.
+- `cli-banner.svg`, `cli.gif` — release artifacts.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,90 +1 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Build & Run
-
-```bash
-# Build the binary (requires CGO for BLS crypto)
-CGO_ENABLED=1 CGO_CFLAGS="-O2 -D__BLST_PORTABLE__ -std=gnu11" GO111MODULE=on go build -o ./cmd/flow/flow ./cmd/flow
-
-# Or use Make
-make binary
-
-# Run directly without building
-go run cmd/flow/main.go [command]
-```
-
-## Testing
-
-```bash
-# Run all tests
-make test
-# Equivalent: CGO_ENABLED=1 CGO_CFLAGS="-O2 -D__BLST_PORTABLE__ -std=gnu11" GO111MODULE=on go test -coverprofile=coverage.txt ./...
-
-# Run a single test package
-CGO_ENABLED=1 CGO_CFLAGS="-O2 -D__BLST_PORTABLE__ -std=gnu11" go test ./internal/accounts/...
-
-# Run a specific test
-CGO_ENABLED=1 CGO_CFLAGS="-O2 -D__BLST_PORTABLE__ -std=gnu11" go test ./internal/accounts/... -run TestFunctionName
-
-# Skip network-dependent tests (e.g. in sandboxed environments)
-SKIP_NETWORK_TESTS=1 make test
-```
-
-## Linting
-
-```bash
-make lint         # Run golangci-lint
-make fix-lint     # Auto-fix lint issues
-make check-headers  # Verify Apache license headers on all Go files
-go generate ./... # Regenerate generated code (required before lint)
-```
-
-## Architecture
-
-The CLI is a [Cobra](https://github.com/spf13/cobra)-based application with three main layers:
-
-### Entry Point
-`cmd/flow/main.go` — wires all subcommands into the root `flow` command.
-
-### Command Framework (`internal/command/`)
-The `command.Command` struct wraps a `cobra.Command` with two execution modes:
-- `Run` — for commands that don't need a loaded `flow.json` state
-- `RunS` — for commands that require an initialized project state (`*flowkit.State`)
-
-`Command.AddToParent()` handles all shared boilerplate: loading `flow.json`, resolving network/host, creating the gRPC gateway, initializing `flowkit.Services`, version checking, analytics, and error formatting. **All new commands should use this pattern.**
-
-Every command's run function returns a `command.Result` interface with three output methods: `String()` (human-readable), `Oneliner()` (grep-friendly inline), and `JSON()` (structured). The framework handles `--output`, `--filter`, and `--save` flags automatically.
-
-### Command Packages (`internal/`)
-Each feature area is its own package with a top-level `Cmd *cobra.Command` that aggregates subcommands. Pattern:
-- `accounts.Cmd` (`internal/accounts/`) — registered in `main.go` via `cmd.AddCommand(accounts.Cmd)`
-- Subcommands (e.g., `get.go`, `create.go`) define a package-level `var getCommand = &command.Command{...}` and register via `init()` or the parent's `init()`
-
-Key packages:
-- `internal/super/` — high-level "super commands": `flow init`, `flow dev`, `flow generate`, `flow flix`
-- `internal/super/generator/` — code generation engine for Cadence contracts, scripts, transactions, and tests
-- `internal/dependencymanager/` — `flow deps` commands for managing on-chain contract dependencies
-- `internal/config/` — `flow config` subcommands for managing `flow.json`
-- `internal/emulator/` — wraps the Flow emulator
-
-### flowkit Dependency
-The CLI delegates all blockchain interactions to the `github.com/onflow/flowkit/v2` module (external). The `flowkit.Services` interface is the primary abstraction for network calls. The local `flowkit/` directory is a historical artifact (migrated to the external module) and contains only a README and schema.
-
-### Global Flags
-Defined in `internal/command/global_flags.go`, applied to every command: `--network`, `--host`, `--log`, `--output`, `--filter`, `--save`, `--config-path`, `--yes`, `--skip-version-check`.
-
-### Configuration
-`flow.json` is the project config file. `flowkit.Load()` reads it. The `internal/config/` commands modify it. `state.Networks()`, `state.Accounts()`, etc. provide typed access.
-
-## CLI Design Conventions
-- Commands follow `noun verb` pattern (`flow accounts get`)
-- Prefer flags over positional args; use args only for the primary required value
-- `--output json` must always work for machine-readable output
-- Errors go to stderr; normal output to stdout
-- Progress indicators for long-running operations via `logger.StartProgress()` / `logger.StopProgress()`
-- Long-running commands support `--yes` to skip confirmation prompts
-
-## License Headers
-All Go source files must have the Apache 2.0 license header. Run `make check-headers` to verify.
+@AGENTS.md
PATCH

echo "Gold patch applied."
