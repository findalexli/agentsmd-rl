#!/usr/bin/env bash
set -euo pipefail

cd /workspace/places

# Idempotency guard
if grep -qF ".github/copilot-instructions.md" ".github/copilot-instructions.md" && grep -qF "- One test file per integration file: every integration source file should have " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,74 +0,0 @@
-# places Home Assistant Integration Copilot Instructions
-
-## General Guidelines
-- Follow Home Assistant's developer documentation: https://developers.home-assistant.io/docs/.
-- Be clear and explain what you are doing while coding; prefer short, actionable explanations.
-- Provide code snippets and targeted tests to validate behavior.
-- Provide a concise plan for non-trivial changes; for small, low-risk edits the agent may implement the change and provide a one-line summary immediately after.
-- Focus on one conceptual change at a time when changes affect public APIs or multiple modules.
-- Include concise explanations of what changed and why.
-- Always check if the edit maintains the project's coding style.
-- Develop for Python 3.13+.
-- Develop with the latest Home Assistant core version.
-- Transparency on deviations: When the agent cannot or chooses not to follow one or more rules in this document, it must explicitly call out which guideline(s) are not being followed and provide a concise reason (for example: system/developer instruction conflict, missing permissions, missing dev dependencies, user denied install/network access, or safety policy). This explanation must appear in the same response turn that performs the deviation.
-
-## Agent permissions and venv policy
-- The agent may create and use a repository-local virtual environment at `./.venv` and should reference the interpreter at `./.venv/bin/python` when running commands.
-- The agent may install packages from repository manifests (for example `requirements-dev.txt`, `pyproject.toml`) into the repo venv without needing additional explicit approval for each run. The agent should prefer installing into `./.venv` rather than the global environment and must avoid performing unnecessary or unrelated network operations.
-
-
-## Folder Structure
-
-- `/custom_components/places`: Contains the integration code.
-- `/tests`: Contains the pytest code.
-- `/README.md`: Is the primary documentation for the integration.
-
-## Project Structure
-- Modular design: distinct files for entity types, services, and utilities.
-- Store constants in a separate `const.py` file.
-- Use a `config_flow.py` file for configuration flows.
-
-## Coding Standards
-- Add typing annotations to all functions and classes, including return types.
-- Add descriptive docstrings to all functions and classes (PEP 257 convention). Update existing docstrings if needed.
-- Keep all existing comments in files.
-- Ensure all imports are put at the top of the file.
-- Pre-commit hooks are configured in `/.pre-commit-config.yaml`.
-- Ruff enforces code style (settings in `/pyproject.toml`).
-- mypy enforces static typing (settings in `/pyproject.toml`).
-
-## Local tooling note
-- This repository uses `pre-commit` (configured in `/.pre-commit-config.yaml`) and `pytest` (configured via `pyproject.toml`) as the primary local tooling for formatting, linting, and tests. Avoid recommending `tox` by default — some development environments may still have user-specific VS Code tasks that reference `tox`, which can be misleading. Prefer instructing contributors to run `pre-commit run --all-files` and `pytest` locally.
-- By default, the agent should run the full pytest suite when tests are requested (the repo is small and full pytest runs are acceptable). If the user specifically asks for a focused test run, the agent may run targeted tests instead.
-- Ensure that pytest and pre-commit are always run locally in the repository venv (`./.venv`) unless the user specifies a different environment.
-
-## Error Handling & Logging
-- Implement robust error handling and debug logging.
-- Do not catch Exception directly; catch specific exceptions instead.
-- Use Home Assistant's built-in logging framework.
-- Fail-safe for missing dev dependencies: If a test run fails due to missing dev/test dependencies (for example pytest plugins or helpers), the agent should either:
-  1. Attempt to install the missing dev dependencies into `./.venv` if installs are permitted, or
-  2. Report the missing package(s) with an exact pip install command and fail gracefully.
-
-## Testing
-- Use pytest (not unittest) and pytest plugins for all tests.
-- Use pytest-homeassistant-custom-component for Home Assistant–specific testing utilities (prefer `MockConfigEntry` for config entries) instead of creating custom ones.
-- All tests must have typing annotations and robust docstrings.
-- Use fixtures and mocks to isolate tests.
-- Use `conftest.py` for shared test utilities and fixtures.
-- Parameterize tests instead of creating multiple similar test functions when appropriate.
-- When parameterizing tests, delete any legacy placeholder tests and related comments.
-- Don't run pytest with `--disable-warnings` and address all warnings.
-- Prefer running the full pytest suite by default for this repository. Only run focused tests when the user explicitly asks for targeted runs.
-- One test file per integration file: every integration source file should have a single corresponding test module; add new unit tests for that integration to that existing test module and do not create additional test modules targeting the same integration except for explicit end-to-end/integration tests in `test_integration.py`.
-- Achieve at least 80% code coverage.
-- When making changes to code, include tests for the new/changed behavior; the agent should add tests alongside code edits even when changes are not minimally invasive.
-
-## PR and branch behavior
-- The agent will only create branches or open PRs when the user explicitly requests it or includes the hashtag `#github-pull-request_copilot-coding-agent` to hand off to the asynchronous coding agent.
-
-## Network / install consent
-- The agent must obtain explicit consent before performing network operations outside the repository that are not strictly necessary for running local tests (for example fetching external APIs or secrets). Package installs from PyPI required for running tests are allowed when the user has given permission to install dev dependencies.
-
-## CI/CD
-- Use GitHub Actions for CI/CD.
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,94 @@
+# AGENTS
+
+## Purpose
+
+- Provide clear, repo-specific instructions for autonomous agents working in this repository.
+
+## General Guidelines
+
+- Follow Home Assistant developer docs: https://developers.home-assistant.io/docs/.
+- Be concise and explain coding steps briefly when making code changes; include code snippets and tests where relevant.
+- For non-trivial edits, provide a short plan. For small, low-risk edits, implement and include a one-line summary.
+- Focus on a single conceptual change at a time when public APIs or multiple modules are affected.
+- Maintain project style and Python 3.13+ compatibility. Target latest Home Assistant core.
+- If deviating from these guidelines, explicitly state which guideline is deviated from and why.
+
+## Agent permissions and venv policy
+
+- Agents may create and use a repository-local venv at `./.venv` and should reference `./.venv/bin/python` when running commands.
+- Installing packages from repo manifests (prefer `pyproject.toml`) into `./.venv` is allowed for running tests or local tooling; avoid unrelated network operations without explicit consent.
+
+## Home Assistant integration hygiene
+
+- When changing config/options text or UI-visible strings:
+  - Update `translations/*.json` as needed.
+- When changing install/config steps:
+  - Update `README.md` and `hacs.json` as needed.
+
+## Folder structure (repo-specific)
+
+- `custom_components/places`: integration code.
+- `tests`: pytest test suite and fixtures.
+- `README.md`: primary documentation.
+
+## Project structure expectations
+
+- Keep code modular: separate files for entity types, services, and utilities.
+- Store constants in `const.py` and use a `config_flow.py` for configuration flows.
+
+## Coding standards
+
+- Add typing annotations to all functions and classes (including return types).
+- Add or update docstrings for all files, classes and methods, including private methods. Method docstrings must be in NumPy format.
+- Preserve existing comments and keep imports at the top of files.
+- When editing code, prefer fixing root causes over surface patches.
+- Keep changes minimal and consistent with the codebase style.
+- Add tests for any changed behavior and update documentation if needed.
+
+## Error handling & logging
+
+- Use Home Assistant's logging framework.
+- Catch specific exceptions (do not catch Exception directly).
+- If a broad catch is unavoidable, document why in a comment and include contextual logging.
+- Add robust error handling and clear debug/info logs.
+
+## Local tooling (common commands)
+
+- Use `pre-commit`, `mypy`, and `pytest` configured in the repo. You must run these inside `./.venv`.
+- Prefer invoking tooling via `./.venv/bin/python -m ...` rather than relying on global/shell entry points (e.g., `pre-commit`).
+- `ruff` is used for linting and formatting but should be called using `pre-commit`.
+- Run tests:
+  - `./.venv/bin/python -m pytest`
+- Run pre-commit on all files (includes `ruff`):
+  - `./.venv/bin/python -m pre_commit run --all-files`
+- Run mypy (use repo configuration):
+  - `./.venv/bin/python -m mypy`
+
+## Testing
+
+- Use pytest (not unittest) and pytest plugins for all tests.
+- Use pytest-homeassistant-custom-component for Home Assistant–specific testing utilities (prefer `MockConfigEntry` for config entries).
+- Parameterize tests instead of creating multiple similar test functions when appropriate.
+- Aim for at least 80% code coverage.
+- Don't run pytest with `--disable-warnings` and address all warnings.
+- By default, the agent should run the full pytest suite when tests are requested (the repo is small and full pytest runs are acceptable). If the user specifically asks for a focused test run, the agent may run targeted tests instead.
+- Use fixtures and mocks to isolate tests.
+- Use `conftest.py` for shared test utilities and fixtures.
+- Add typed, well-documented tests in `tests/` and use fixtures in `conftest.py`. Test documentation must use NumPy format.
+- One test file per integration file: every integration source file should have a single corresponding test module; add new unit tests for that integration to that existing test module. Only split into additional test modules if the existing test module would exceed ~1000 lines, except for explicit end-to-end/integration tests in `test_integration.py`.
+- If tests fail due to missing dev dependencies, install them into `./.venv` and add them into the `pyproject.toml` dependencies when appropriate.
+- When parameterizing tests, delete any legacy placeholder tests and related comments.
+- When making changes to code, include tests for the new/changed behavior; the agent should add tests alongside code edits even when changes are not minimally invasive.
+
+## PR and branch behavior
+
+- The agent will only create branches or open PRs when the user explicitly requests it or includes the hashtag `#github-pull-request_copilot-coding-agent` to hand off to the asynchronous coding agent.
+
+## Network / install consent
+
+- Obtain explicit consent before any network operations outside the repository not strictly needed to run local tests.
+- Package installs required for running tests are allowed when user approves.
+
+## CI/CD
+
+- Use GitHub Actions for CI/CD where applicable.
PATCH

echo "Gold patch applied."
