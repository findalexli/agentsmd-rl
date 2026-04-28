#!/usr/bin/env bash
set -euo pipefail

cd /workspace/software-agent-sdk

# Idempotency guard
if grep -qF "- Tool names, parameter schemas, and output schemas are user-facing and often re" "openhands-tools/openhands/tools/AGENTS.md" && grep -qF "- The published import surface is `openhands-workspace/openhands/workspace/__ini" "openhands-workspace/openhands/workspace/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/openhands-tools/openhands/tools/AGENTS.md b/openhands-tools/openhands/tools/AGENTS.md
@@ -0,0 +1,30 @@
+# Repository Guidelines
+
+## Project Structure & Module Organization
+
+- This directory (`openhands-tools/openhands/tools/`) contains runtime tool implementations under the `openhands.tools.*` namespace.
+- Most tools live in dedicated subpackages (for example `terminal/`, `file_editor/`, `browser_use/`) and typically split:
+  - `definition.py`: public schema/metadata/registration
+  - `impl.py` / `core.py`: runtime implementation
+- Treat `openhands-tools/openhands/tools/__init__.py` as the published surface for `openhands-tools`; `__all__` is considered public API.
+
+## Build, Test, and Development Commands
+
+- `make build`: set up the dev environment (`uv sync --dev`) and install pre-commit hooks.
+- `uv run pre-commit run --files <path>`: run checks only for the files you touched.
+- `uv run pytest tests/tools -k <pattern>`: run the tools test suite; prefer running a focused subset first (e.g. `uv run pytest tests/tools/terminal`).
+
+## Coding Style & Naming Conventions
+
+- Python target is 3.12; keep code Ruff-compliant (line length 88) and Pyright-friendly.
+- Tool names, parameter schemas, and output schemas are user-facing and often referenced in tests like `tests/tools/test_tool_name_consistency.py`; avoid breaking changes. If a schema must change, provide a backward-compatible loading path.
+- When adding runtime-loaded assets (Jinja `.j2` templates or JS under `browser_use/js/`), ensure they are included as package data (and update the agent-server PyInstaller spec when needed).
+
+## Testing Guidelines
+
+- Add/adjust unit tests under `tests/tools/`, mirroring the tool package. Keep tests focused on the behavior you changed.
+- Prefer real code paths over mocks; when mocking is unavoidable (e.g. external processes), centralize setup in `tests/conftest.py` or `tests/tools/<tool>/conftest.py`.
+
+## Commit & Pull Request Guidelines
+
+- Keep changes scoped to the tool(s) touched, and run the smallest relevant tests before running broader suites.
diff --git a/openhands-workspace/openhands/workspace/AGENTS.md b/openhands-workspace/openhands/workspace/AGENTS.md
@@ -0,0 +1,28 @@
+# Repository Guidelines
+
+## Project Structure & Module Organization
+
+- This directory (`openhands-workspace/openhands/workspace/`) contains workspace implementations under the `openhands.workspace.*` namespace (Docker, Apptainer, cloud, and API-remote).
+- Each backend lives in its own subpackage (e.g. `docker/`, `cloud/`) and typically exposes a `*Workspace` class from `workspace.py`.
+- The published import surface is `openhands-workspace/openhands/workspace/__init__.py` (`__all__` is treated as public API). Keep imports lightweight so `import openhands.workspace` does not pull in build-time dependencies.
+- These classes should remain compatible with the SDK workspace interfaces and types (for example `openhands.sdk.workspace.RemoteWorkspace`, `TargetType`, `PlatformType`).
+
+## Build, Test, and Development Commands
+
+- `make build`: set up the dev environment (`uv sync --dev`) and install pre-commit hooks.
+- `uv run pre-commit run --files <path>`: run checks for only the files you changed.
+- `uv run pytest tests/workspace -k <pattern>`: run workspace tests; start with the narrowest file/directory that covers your change.
+
+## Coding Style & Naming Conventions
+
+- Python target is 3.12; keep code Ruff-compliant (line length 88) and Pyright-friendly.
+- Prefer small, explicit wrappers around external interactions (Docker/Apptainer/HTTP). Validate inputs early and keep side-effecting operations out of module import time.
+
+## Testing Guidelines
+
+- Tests live under `tests/workspace/` and generally validate import behavior, model fields, and command invocation. Prefer patching command executors instead of requiring real Docker in unit tests.
+- Add focused coverage for backend-specific behavior and for any changes that affect the public import surface.
+
+## Commit & Pull Request Guidelines
+
+- Avoid breaking changes to exported workspace classes/symbols; deprecate before removal when changing the public surface.
PATCH

echo "Gold patch applied."
