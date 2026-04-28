#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rattler

# Idempotency guard
if grep -qF "../AGENTS.md" ".claude/CLAUDE.md" && grep -qF "- Rust monorepo for conda package management (solving, installing, fetching repo" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -0,0 +1 @@
+../AGENTS.md
\ No newline at end of file
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,5 @@
+- Rust monorepo for conda package management (solving, installing, fetching repodata), used by pixi, rattler-build, prefix.dev
+- Build: `pixi run build` | Test: `pixi run test` | Lint all: `pixi run lint`
+- Single test: `pixi run -- cargo nextest run -p <crate_name> <test_name>`
+- Before committing, run `pixi run cargo-fmt` and `pixi run cargo-clippy` to ensure formatting and lint compliance
+- crates in `crates/`, Python bindings in `py-rattler/`, WASM bindings in `js-rattler/`
PATCH

echo "Gold patch applied."
