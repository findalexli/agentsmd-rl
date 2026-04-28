#!/usr/bin/env bash
set -euo pipefail

cd /workspace/software-agent-sdk

# Idempotency guard
if grep -qF "- This is a `uv`-managed Python monorepo (single `uv.lock` at repo root) with mu" "AGENTS.md" && grep -qF "## Package Structure & Module Organization" "openhands-sdk/openhands/sdk/AGENTS.md" && grep -qF "## Package Structure & Module Organization" "openhands-tools/openhands/tools/AGENTS.md" && grep -qF "## Package Structure & Module Organization" "openhands-workspace/openhands/workspace/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -315,7 +315,7 @@ These are enforced by `check_sdk_api_breakage.py` (runs on release PRs). Depreca
 - AFTER you edit ONE file, you should run pre-commit hook on that file via `uv run pre-commit run --files [filepath]` to make sure you didn't break it.
 - Don't write TOO MUCH test, you should write just enough to cover edge cases.
 - Check how we perform tests in .github/workflows/tests.yml
-- You should put unit tests in the corresponding test folder. For example, to test `openhands.sdk.tool/tool.py`, you should put tests under `openhands.sdk.tests/tool/test_tool.py`.
+- Put unit tests under the corresponding domain folder in `tests/` (e.g., `tests/sdk`, `tests/tools`, `tests/workspace`). For example, changes to `openhands-sdk/openhands/sdk/tool/tool.py` should be covered in `tests/sdk/tool/test_tool.py`.
 - DON'T write TEST CLASSES unless absolutely necessary!
 - If you find yourself duplicating logics in preparing mocks, loading data etc, these logic should be fixtures in conftest.py!
 - Please test only the logic implemented in the current codebase. Do not test functionality (e.g., BaseModel.model_dumps()) that is not implemented in this repository.
@@ -370,7 +370,8 @@ Note: This is separate from `persistence_dir` which is used for conversation sta
 
 <REPO>
 <PROJECT_STRUCTURE>
-- `openhands-sdk/` core SDK; `openhands-tools/` built-in tools; `openhands-workspace/` workspace management; `openhands-agent-server/` server runtime; `examples/` runnable patterns; `tests/` split by domain (`tests/sdk`, `tests/tools`, `tests/agent_server`, etc.).
+- This is a `uv`-managed Python monorepo (single `uv.lock` at repo root) with multiple distributable packages: `openhands-sdk/` (SDK), `openhands-tools/` (built-in tools), `openhands-workspace/` (workspace impls), and `openhands-agent-server/` (server runtime).
+- `examples/` contains runnable patterns; `tests/` is split by domain (`tests/sdk`, `tests/tools`, `tests/workspace`, `tests/agent_server`, etc.).
 - Python namespace is `openhands.*` across packages; keep new modules within the matching package and mirror test paths under `tests/`.
 </PROJECT_STRUCTURE>
 
diff --git a/openhands-sdk/openhands/sdk/AGENTS.md b/openhands-sdk/openhands/sdk/AGENTS.md
@@ -1,6 +1,6 @@
-# Repository Guidelines
+# Package Guidelines
 
-## Project Structure & Module Organization
+## Package Structure & Module Organization
 
 - This directory (`openhands-sdk/openhands/sdk/`) contains the core Python SDK under the `openhands.sdk.*` namespace.
 - Keep new modules within the closest existing subpackage (e.g., `llm/`, `tool/`, `event/`, `agent/`) and follow local naming patterns.
diff --git a/openhands-tools/openhands/tools/AGENTS.md b/openhands-tools/openhands/tools/AGENTS.md
@@ -1,6 +1,6 @@
-# Repository Guidelines
+# Package Guidelines
 
-## Project Structure & Module Organization
+## Package Structure & Module Organization
 
 - This directory (`openhands-tools/openhands/tools/`) contains runtime tool implementations under the `openhands.tools.*` namespace.
 - Most tools live in dedicated subpackages (for example `terminal/`, `file_editor/`, `browser_use/`) and typically split:
diff --git a/openhands-workspace/openhands/workspace/AGENTS.md b/openhands-workspace/openhands/workspace/AGENTS.md
@@ -1,6 +1,6 @@
-# Repository Guidelines
+# Package Guidelines
 
-## Project Structure & Module Organization
+## Package Structure & Module Organization
 
 - This directory (`openhands-workspace/openhands/workspace/`) contains workspace implementations under the `openhands.workspace.*` namespace (Docker, Apptainer, cloud, and API-remote).
 - Each backend lives in its own subpackage (e.g. `docker/`, `cloud/`) and typically exposes a `*Workspace` class from `workspace.py`.
PATCH

echo "Gold patch applied."
