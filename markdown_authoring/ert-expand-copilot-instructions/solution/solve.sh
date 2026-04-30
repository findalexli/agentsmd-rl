#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ert

# Idempotency guard
if grep -qF "- Plugin system lives under `src/ert/plugins` (hook specs + implementations + ru" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,3 +1,75 @@
+# Copilot instructions for `ert`
+
+## Build, test, lint, and type-check commands
+
+Use `uv` for all local commands (this repo is managed with `uv sync` groups).
+
+```bash
+# Dev environment
+uv sync --all-groups
+
+# Fast local regression checks (same target used by pre-push hook)
+uv run just rapid-tests
+
+# Full local check bundle (tests + typing + docs builds)
+uv run just check-all
+
+# ERT-focused suites
+uv run just ert-unit-tests
+uv run just ert-cli-tests
+uv run just ert-gui-tests
+
+# Everest suite
+uv run just everest-tests
+
+# Type checking
+uv run just check-types
+# (equivalent to: uv run mypy src)
+
+# Style/lint hooks used in CI
+SKIP=no-commit-to-branch uv run pre-commit run --all-files --hook-stage pre-push
+
+# Docs
+uv run just build-ert-docs
+uv run just build-everest-docs
+```
+
+Run a single test:
+
+```bash
+uv run pytest tests/ert/unit_tests/<path>/test_<file>.py::test_<name>
+uv run pytest tests/everest/test_<file>.py::test_<name>
+```
+
+## High-level architecture
+
+- `src/ert`: main application package (CLI + GUI + analysis workflows + storage integration).
+  - Entry point: `ert` script -> `src/ert/__main__.py`.
+  - `ert` subcommands include GUI, lint, API server, and running in CLI.
+  - `ert.services._storage_main` starts the storage server (uvicorn).
+  - `ert.dark_storage` contains the FastAPI app/endpoints used by the storage/API layer.
+- `src/everest`: optimization tool built on top of ERT.
+  - Entry point for `everest`: `src/everest/bin/main.py`.
+  - `everest/optimizer` converts the Everest model/configuration into `ropt`.
+- `src/_ert`: shared low-level runtime helpers (e.g., threading/forward-model runner support).
+- Plugin system lives under `src/ert/plugins` (hook specs + implementations + runtime plugin loading); `ert.__main__` executes within runtime plugin context.
+- Tests are split by intent:
+  - `tests/ert/unit_tests` (fast/reliable), `tests/ert/ui_tests` (cli/gui behavior), `tests/ert/performance_tests`, and `tests/everest`.
+
+## Key repository conventions
+
+- Prefer `just` targets for standardized test groupings and CI parity (`rapid-tests`, `check-all`, `ert-*`, `everest-tests`).
+- Keep unit tests in `tests/ert/unit_tests` exceptionally fast; slower/broader cases should be marked with `@pytest.mark.integration_test` or moved.
+- Test naming convention in this repo is explicit behavior-driven names (often `test_that_...`), not vague names like `test_works`.
+- Type-hint policy from `CONTRIBUTING.md`:
+  - avoid `Any` when possible,
+  - use `@override` for overridden non-dunder methods,
+  - prefer `cast`/`assert` over blanket `# type: ignore`.
+- Pre-commit is the source of truth for formatting/lint hooks (`ruff-check --fix`, `ruff-format`, yaml/json checks, actionlint, lockfile checks).
+- Some test data requires LFS/submodules (`git lfs install` and `git submodule update --init --recursive`) for representative local runs.
+
+---
+
 # Copilot Code Review Instructions
 
 Apply these instructions only when performing a code review for this repository.
PATCH

echo "Gold patch applied."
