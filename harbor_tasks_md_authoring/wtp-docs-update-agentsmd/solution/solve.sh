#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wtp

# Idempotency guard
if grep -qF "- Internal packages: `internal/{git,config,hooks,command,errors,io,testutil}`." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -7,7 +7,7 @@
 ## Project Structure & Modules
 - Root module: `github.com/satococoa/wtp/v2` (Go 1.24).
 - CLI entrypoint: `cmd/wtp`.
-- Internal packages: `internal/{git,config,hooks,command,errors,io}`.
+- Internal packages: `internal/{git,config,hooks,command,errors,io,testutil}`.
 - Tests: unit tests alongside packages (`*_test.go`), end-to-end tests in `test/e2e`.
 - Tooling/config: `.golangci.yml`, `.goreleaser.yml`, `Taskfile.yml`, `.wtp.yml` (project hooks), `docs/`.
 
@@ -53,7 +53,6 @@
 ### Quick Testing Tips
 - Use `go run ./cmd/wtp <args>` for rapid feedback instead of building binaries.
 - Run commands from inside a worktree to mimic real usage (e.g., `go run ../cmd/wtp add feature/new-feature`).
-- Toggle shell integration paths with `WTP_SHELL_INTEGRATION=1` when testing cd behavior.
 
 ### Testing Strategy
 - Unit tests target 70% of coverage: fast feedback, mocked git interactions, table-driven cases.
PATCH

echo "Gold patch applied."
