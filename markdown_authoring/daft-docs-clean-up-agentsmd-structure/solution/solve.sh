#!/usr/bin/env bash
set -euo pipefail

cd /workspace/daft

# Idempotency guard
if grep -qF "- Titles: Conventional Commits format; enforced by `.github/workflows/pr-labelle" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,20 +1,18 @@
-# AGENTS.md
-
-## Resources
+# Resources
 
 - https://docs.daft.ai for the user-facing API docs
 - CONTRIBUTING.md for detailed development process
 - https://github.com/Eventual-Inc/Daft for issues, discussions, and PRs
 
-## Dev Workflow
+# Dev Workflow
 
 1) [Once] Set up Python environment and install dependencies: `make .venv`
 2) [Optional] Activate .venv: `source .venv/bin/activate`. Not necessary with Makefile commands.
 3) If Rust code is modified, rebuild: `make build`
 4) If `.proto` files are modified, rebuild protocol buffers code: `make daft-proto`
 5) Run tests. See [Testing Details](#testing-details).
 
-## Testing Details
+# Testing Details
 
 - `make test` runs tests in `tests/` directory. Uses `pytest` under the hood.
   - Must set `DAFT_RUNNER` environment variable to `ray` or `native` to run the tests with the corresponding runner.
@@ -25,7 +23,7 @@
   -  Default `integration`, `benchmark`, and `hypothesis` tests are disabled. Best to run on CI.
 - `make doctests` runs doctests in `daft/` directory. Tests docstrings in Daft APIs.
 
-## PR Conventions
+# PR Conventions
 
-- Titles: Conventional Commits (e.g., `feat: ...`); enforced by `.github/workflows/pr-labeller.yml`.
+- Titles: Conventional Commits format; enforced by `.github/workflows/pr-labeller.yml`.
 - Descriptions: follow `.github/pull_request_template.md`.
PATCH

echo "Gold patch applied."
