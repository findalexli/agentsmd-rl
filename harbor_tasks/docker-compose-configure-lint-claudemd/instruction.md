# Configure lint rules and fix style issues in Docker Compose

## Problem

The project has several Go style issues that a modern linter would flag:

1. `pkg/compose/publish.go` uses the anti-pattern `WriteString(fmt.Sprintf(...))` in three places. Go's `fmt.Fprintf` writes formatted output directly to an `io.Writer` — it is more efficient and idiomatic than allocating a string with `fmt.Sprintf` and then writing it.

2. `pkg/e2e/compose_run_build_once_test.go` contains a `//nolint:errcheck` directive that suppresses a legitimate lint warning unnecessarily. The directive should be removed.

3. The project's `Dockerfile` pins `GOLANGCI_LINT_VERSION` to an outdated version. It should be bumped to `v2.11.3`.

4. The project lacks a `CLAUDE.md` file to guide contributors and tooling on build, test, and code style conventions.

## Expected Behavior

- All `WriteString(fmt.Sprintf(...))` calls in `publish.go` should be replaced with the equivalent `fmt.Fprintf(&builder, ...)` calls
- The `//nolint:errcheck` comment in the test file should be removed
- The `GOLANGCI_LINT_VERSION` in `Dockerfile` should be bumped
- A `CLAUDE.md` file should be created at the project root documenting:
  - Build and test commands (`make build`, `make test`, `go test` targets)
  - Linting setup (golangci-lint v2, `.golangci.yml` config, how to run it)
  - Code style conventions (formatting, import order, banned packages, preferred patterns like `fmt.Fprintf` over `WriteString(fmt.Sprintf(...))`)

## Files to Look At

- `pkg/compose/publish.go` — contains three `WriteString(fmt.Sprintf(...))` calls that need refactoring
- `pkg/e2e/compose_run_build_once_test.go` — has an unnecessary `//nolint:errcheck` directive
- `Dockerfile` — pins the golangci-lint version (look for `GOLANGCI_LINT_VERSION`)
- `.golangci.yml` — existing linter configuration, useful reference for documenting conventions
- `CLAUDE.md` — does not exist yet; should be created
