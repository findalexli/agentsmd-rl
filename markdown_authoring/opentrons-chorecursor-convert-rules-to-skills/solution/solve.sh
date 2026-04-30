#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opentrons

# Idempotency guard
if grep -qF ".cursor/rules/ai-server.mdc" ".cursor/rules/ai-server.mdc" && grep -qF "`opentrons-ai-server` is a standalone FastAPI service for Opentrons AI \u2014 protoco" ".cursor/skills/ai-server/SKILL.md" && grep -qF "description: Conventions for the analyses snapshot testing framework in analyses" ".cursor/skills/analyses-snapshot-testing/SKILL.md" && grep -qF "description: ProtocolDeck component testing environment using built packages wit" ".cursor/skills/components-testing/SKILL.md" && grep -qF "description: CSS Modules conventions, Stylelint rules, design tokens (spacing, c" ".cursor/skills/css-modules/SKILL.md" && grep -qF "description: E2E testing conventions for Protocol Designer and Labware Library u" ".cursor/skills/e2e-testing/SKILL.md" && grep -qF "description: Locize i18n synchronization workflow for pushing and downloading tr" ".cursor/skills/locize-sync/SKILL.md" && grep -qF "description: TypeScript conventions, React patterns, testing, styling, and impor" ".cursor/skills/opentrons-typescript/SKILL.md" && grep -qF "Protocol Designer (PD) is a React + Redux + React Router + TypeScript web app fo" ".cursor/skills/protocol-designer/SKILL.md" && grep -qF "General TypeScript, React, styling, testing, and import conventions are in the `" ".cursor/skills/react-component-creation/SKILL.md" && grep -qF "description: Guidelines for robot Python projects \u2014 api/, robot-server/, hardwar" ".cursor/skills/robot-python-projects/SKILL.md" && grep -qF "description: Conventions for static deploy automation Python CLIs in scripts/sta" ".cursor/skills/static-deploy/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/ai-server.mdc b/.cursor/rules/ai-server.mdc
@@ -1,158 +0,0 @@
----
-description: Conventions for the opentrons-ai-server FastAPI service
-globs: opentrons-ai-server/**
-alwaysApply: false
----
-
-# AI Server Instructions
-
-## Overview
-
-`opentrons-ai-server` is a standalone FastAPI service for Opentrons AI — protocol generation, chat completions, and related AI features. It is **not** part of the monorepo build system; it has its own dependency management, CI workflows, and deployment pipeline.
-
-Deployed environments: **staging** (`staging.opentrons.ai`) and **prod** (`ai.opentrons.com`), running on AWS ECS Fargate behind CloudFront.
-
-## Package Manager — uv
-
-This project uses **uv** for Python dependency management (not pipenv, pip-tools, or poetry).
-
-| File | Role | Committed? |
-| --- | --- | --- |
-| `pyproject.toml` | Single source of truth for dependencies AND all tool config | Yes |
-| `uv.lock` | Locked dependency graph | Yes |
-| `requirements.txt` | Generated pip-format file for Docker builds | No (gitignored) |
-| `.venv/` | Local virtual environment created by `uv sync` | No (gitignored) |
-
-### Key Commands
-
-```bash
-make setup                    # Install all deps (uv sync --frozen)
-uv add <package>              # Add production dep
-uv add --dev <package>        # Add dev-only dep
-uv remove <package>           # Remove dep
-uv lock                       # Re-resolve after manual pyproject.toml edits
-uv run <command>              # Run inside the managed venv
-```
-
-After changing deps, **commit both** `pyproject.toml` and `uv.lock`.
-
-## Project Structure
-
-```
-opentrons-ai-server/
-├── api/                        # Application source code
-│   ├── handler/                # FastAPI app, routes, middleware (fast.py entrypoint)
-│   ├── domain/                 # Business logic — LLM prediction (Anthropic, OpenAI)
-│   ├── models/                 # Pydantic request/response models
-│   ├── services/               # File processing and other services
-│   ├── integration/            # External integrations (Auth0, Google Sheets, AWS)
-│   ├── constants/              # Shared constants
-│   ├── data/                   # Static data files
-│   ├── storage/                # Stored API docs, indexes
-│   ├── utils/                  # Markdown conversion, index creation
-│   └── settings.py             # Pydantic Settings — all env vars and secrets
-├── tests/
-│   ├── conftest.py             # Pytest fixtures and --env option
-│   ├── helpers/                # Client, token helpers for live testing
-│   └── test_*.py               # Unit and live tests
-├── deploy.py                   # ECS Fargate deployment script
-├── Dockerfile
-├── Makefile
-├── pyproject.toml
-└── uv.lock
-```
-
-## Configuration & Settings
-
-All runtime configuration lives in `api/settings.py` via `pydantic-settings`:
-
-- **Locally**: values come from a `.env` file (gitignored)
-- **Deployed**: values come from AWS Secrets Manager, loaded into ECS by `deploy.py`
-- Every new env var or secret **must** be added as a field on the `Settings` class
-- Secrets use `SecretStr` type; non-secret vars are plain strings with defaults
-
-Generate a template `.env` from defaults: `make gen-env`
-
-## Tool Configuration
-
-All config is in `pyproject.toml` — no separate config files:
-
-| Tool | Section | Purpose |
-| --- | --- | --- |
-| ruff | `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]` | Linting AND formatting |
-| mypy | `[tool.mypy]`, `[[tool.mypy.overrides]]` | Strict type checking with pydantic plugin |
-| pytest | `[tool.pytest.ini_options]` | Test runner config, markers: `unit`, `live` |
-
-Line length: **140**. Target: **Python 3.12**. Mypy is in **strict** mode.
-
-## Makefile Targets
-
-All targets run from `opentrons-ai-server/`.
-
-### Development
-
-| Target | Description |
-| --- | --- |
-| `make setup` | Install all deps (`uv sync --frozen --extra dev`) |
-| `make teardown` | Delete `.venv/` |
-| `make format` | Auto-fix lint + format with ruff, then prettier for .md/.json |
-| `make lint` | Check lint (ruff) + type check (mypy) — no auto-fix |
-| `make prep` | `format` then `lint` then `unit-test` |
-| `make unit-test` | Run unit tests (`pytest tests -m unit`) |
-
-### Running Locally
-
-| Target | Description |
-| --- | --- |
-| `make local-run` | Run FastAPI with uvicorn (hot reload, no Docker) |
-| `make build` | Generate requirements.txt, build Docker image |
-| `make run` | Run the Docker container (requires `.env` file) |
-| `make rebuild` | `clean` + `build` + `run` |
-| `make live-test` | Run live tests against a running server (`ENV=local` default) |
-| `make live-client` | Interactive client for testing the API |
-
-### Deployment
-
-| Target | Description |
-| --- | --- |
-| `make gen-requirements` | Export `uv.lock` to `requirements.txt` (production deps only) |
-| `make deploy ENV=staging` | Build, push to ECR, update ECS service |
-| `make dry-deploy ENV=staging` | Retrieve AWS data but make no changes |
-| `make build-only ENV=staging` | Build Docker image only, no push/deploy |
-
-## Docker Build
-
-The container does **not** use uv internally:
-
-1. `make build` calls `make gen-requirements` → `uv export --no-hashes --no-dev -o requirements.txt`
-2. Dockerfile installs with plain `pip`
-3. Copies `api/` source and Opentrons API docs
-4. Entrypoint: `uvicorn api.handler.fast:app` (3 workers, port 8000)
-
-Docker build context is the **repo root** (not `opentrons-ai-server/`) so the Dockerfile can copy `api/docs/v2` from the sibling `api/` package.
-
-## Testing
-
-- **Unit tests** (`@pytest.mark.unit`): run offline → `make unit-test`
-- **Live tests** (`@pytest.mark.live`): run against a real server → `make live-test ENV=local`
-- The `--env` pytest option selects the target environment (local/staging/prod)
-- Test helpers in `tests/helpers/` handle Auth0 token caching and HTTP client setup
-
-## Authentication
-
-Auth0 JWT verification via `api/integration/auth.py`. Config: `auth0_domain`, `auth0_api_audience`, `auth0_issuer`, `auth0_algorithms` in Settings.
-
-## Code Conventions
-
-- Formatting and linting: **ruff only** (no black). `make format` to auto-fix
-- Type annotations: **required everywhere** — mypy strict mode
-- Pydantic models for all request/response schemas (in `api/models/`)
-- Structured logging via `structlog`
-- Import sorting handled by ruff's `I` rule (isort-compatible)
-
-## Adding a New Env Var or Secret
-
-1. Add the field to the `Settings` class in `api/settings.py` (use `SecretStr` for secrets)
-2. Add the value to your local `.env` file
-3. Before deploying: add the value in **AWS Secrets Manager** under the environment's secret name
-4. Re-deploy — the deploy script maps Settings fields to ECS container env vars automatically
diff --git a/.cursor/skills/ai-server/SKILL.md b/.cursor/skills/ai-server/SKILL.md
@@ -0,0 +1,157 @@
+---
+name: ai-server
+description: Conventions for the opentrons-ai-server FastAPI service — project structure, uv dependency management, settings, testing, Docker, and deployment. Use when working with files in opentrons-ai-server/ or discussing the AI server API.
+---
+
+# AI Server Instructions
+
+## Overview
+
+`opentrons-ai-server` is a standalone FastAPI service for Opentrons AI — protocol generation, chat completions, and related AI features. It is **not** part of the monorepo build system; it has its own dependency management, CI workflows, and deployment pipeline.
+
+Deployed environments: **staging** (`staging.opentrons.ai`) and **prod** (`ai.opentrons.com`), running on AWS ECS Fargate behind CloudFront.
+
+## Package Manager — uv
+
+This project uses **uv** for Python dependency management (not pipenv, pip-tools, or poetry).
+
+| File               | Role                                                        | Committed?      |
+| ------------------ | ----------------------------------------------------------- | --------------- |
+| `pyproject.toml`   | Single source of truth for dependencies AND all tool config | Yes             |
+| `uv.lock`          | Locked dependency graph                                     | Yes             |
+| `requirements.txt` | Generated pip-format file for Docker builds                 | No (gitignored) |
+| `.venv/`           | Local virtual environment created by `uv sync`              | No (gitignored) |
+
+### Key Commands
+
+```bash
+make setup                    # Install all deps (uv sync --frozen)
+uv add <package>              # Add production dep
+uv add --dev <package>        # Add dev-only dep
+uv remove <package>           # Remove dep
+uv lock                       # Re-resolve after manual pyproject.toml edits
+uv run <command>              # Run inside the managed venv
+```
+
+After changing deps, **commit both** `pyproject.toml` and `uv.lock`.
+
+## Project Structure
+
+```markdown
+opentrons-ai-server/
+├── api/ # Application source code
+│ ├── handler/ # FastAPI app, routes, middleware (fast.py entrypoint)
+│ ├── domain/ # Business logic — LLM prediction (Anthropic, OpenAI)
+│ ├── models/ # Pydantic request/response models
+│ ├── services/ # File processing and other services
+│ ├── integration/ # External integrations (Auth0, Google Sheets, AWS)
+│ ├── constants/ # Shared constants
+│ ├── data/ # Static data files
+│ ├── storage/ # Stored API docs, indexes
+│ ├── utils/ # Markdown conversion, index creation
+│ └── settings.py # Pydantic Settings — all env vars and secrets
+├── tests/
+│ ├── conftest.py # Pytest fixtures and --env option
+│ ├── helpers/ # Client, token helpers for live testing
+│ └── test\_\*.py # Unit and live tests
+├── deploy.py # ECS Fargate deployment script
+├── Dockerfile
+├── Makefile
+├── pyproject.toml
+└── uv.lock
+```
+
+## Configuration & Settings
+
+All runtime configuration lives in `api/settings.py` via `pydantic-settings`:
+
+- **Locally**: values come from a `.env` file (gitignored)
+- **Deployed**: values come from AWS Secrets Manager, loaded into ECS by `deploy.py`
+- Every new env var or secret **must** be added as a field on the `Settings` class
+- Secrets use `SecretStr` type; non-secret vars are plain strings with defaults
+
+Generate a template `.env` from defaults: `make gen-env`
+
+## Tool Configuration
+
+All config is in `pyproject.toml` — no separate config files:
+
+| Tool   | Section                                                 | Purpose                                     |
+| ------ | ------------------------------------------------------- | ------------------------------------------- |
+| ruff   | `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]` | Linting AND formatting                      |
+| mypy   | `[tool.mypy]`, `[[tool.mypy.overrides]]`                | Strict type checking with pydantic plugin   |
+| pytest | `[tool.pytest.ini_options]`                             | Test runner config, markers: `unit`, `live` |
+
+Line length: **140**. Target: **Python 3.12**. Mypy is in **strict** mode.
+
+## Makefile Targets
+
+All targets run from `opentrons-ai-server/`.
+
+### Development
+
+| Target           | Description                                                   |
+| ---------------- | ------------------------------------------------------------- |
+| `make setup`     | Install all deps (`uv sync --frozen --extra dev`)             |
+| `make teardown`  | Delete `.venv/`                                               |
+| `make format`    | Auto-fix lint + format with ruff, then prettier for .md/.json |
+| `make lint`      | Check lint (ruff) + type check (mypy) — no auto-fix           |
+| `make prep`      | `format` then `lint` then `unit-test`                         |
+| `make unit-test` | Run unit tests (`pytest tests -m unit`)                       |
+
+### Running Locally
+
+| Target             | Description                                                   |
+| ------------------ | ------------------------------------------------------------- |
+| `make local-run`   | Run FastAPI with uvicorn (hot reload, no Docker)              |
+| `make build`       | Generate requirements.txt, build Docker image                 |
+| `make run`         | Run the Docker container (requires `.env` file)               |
+| `make rebuild`     | `clean` + `build` + `run`                                     |
+| `make live-test`   | Run live tests against a running server (`ENV=local` default) |
+| `make live-client` | Interactive client for testing the API                        |
+
+### Deployment
+
+| Target                        | Description                                                   |
+| ----------------------------- | ------------------------------------------------------------- |
+| `make gen-requirements`       | Export `uv.lock` to `requirements.txt` (production deps only) |
+| `make deploy ENV=staging`     | Build, push to ECR, update ECS service                        |
+| `make dry-deploy ENV=staging` | Retrieve AWS data but make no changes                         |
+| `make build-only ENV=staging` | Build Docker image only, no push/deploy                       |
+
+## Docker Build
+
+The container does **not** use uv internally:
+
+1. `make build` calls `make gen-requirements` → `uv export --no-hashes --no-dev -o requirements.txt`
+2. Dockerfile installs with plain `pip`
+3. Copies `api/` source and Opentrons API docs
+4. Entrypoint: `uvicorn api.handler.fast:app` (3 workers, port 8000)
+
+Docker build context is the **repo root** (not `opentrons-ai-server/`) so the Dockerfile can copy `api/docs/v2` from the sibling `api/` package.
+
+## Testing
+
+- **Unit tests** (`@pytest.mark.unit`): run offline → `make unit-test`
+- **Live tests** (`@pytest.mark.live`): run against a real server → `make live-test ENV=local`
+- The `--env` pytest option selects the target environment (local/staging/prod)
+- Test helpers in `tests/helpers/` handle Auth0 token caching and HTTP client setup
+
+## Authentication
+
+Auth0 JWT verification via `api/integration/auth.py`. Config: `auth0_domain`, `auth0_api_audience`, `auth0_issuer`, `auth0_algorithms` in Settings.
+
+## Code Conventions
+
+- Formatting and linting: **ruff only** (no black). `make format` to auto-fix
+- Type annotations: **required everywhere** — mypy strict mode
+- Pydantic models for all request/response schemas (in `api/models/`)
+- Structured logging via `structlog`
+- Import sorting handled by ruff's `I` rule (isort-compatible)
+
+## Adding a New Env Var or Secret
+
+1. Add the field to the `Settings` class in `api/settings.py` (use `SecretStr` for secrets)
+2. Add the value to your local `.env` file
+3. Before deploying: add the value in **AWS Secrets Manager** under the environment's secret name
+4. Re-deploy — the deploy script maps Settings fields to ECS container env vars automatically
diff --git a/.cursor/skills/analyses-snapshot-testing/SKILL.md b/.cursor/skills/analyses-snapshot-testing/SKILL.md
@@ -1,7 +1,6 @@
 ---
-description: Conventions for the analyses snapshot testing framework
-globs: analyses-snapshot-testing/**
-alwaysApply: false
+name: analyses-snapshot-testing
+description: Conventions for the analyses snapshot testing framework in analyses-snapshot-testing/. Use when working with protocol analysis snapshots, adding protocols, updating snapshots, or running snapshot tests.
 ---
 
 # Analyses Snapshot Testing Instructions
@@ -28,8 +27,8 @@ The `analyses-snapshot-testing` directory validates that protocol analysis outpu
 
 ## Protocol Naming Convention
 
-```
-{Robot}_{Status}_{Version}_{Source}_{Pipettes}_{Modules}_{Overrides}_{Description}
+```markdown
+{Robot}_{Status}_{Version}_{Source}_{Pipettes}_{Modules}_{Overrides}\_{Description}
 ```
 
 - **Robot**: `OT2` or `Flex`
@@ -133,6 +132,7 @@ make analyze-chunk CHUNK=chunk_0.json  # Analyze specific chunk
 ## CI/CD Integration
 
 Workflow (`analyses-snapshot-test.yaml`) triggers on:
+
 - PRs affecting `api/`, `shared-data/`, or this directory
 - Scheduled daily at 7:26 AM UTC
 - Manual dispatch
diff --git a/.cursor/skills/components-testing/SKILL.md b/.cursor/skills/components-testing/SKILL.md
@@ -1,7 +1,6 @@
 ---
-description: ProtocolDeck component testing environment using built packages with Playwright snapshots
-globs: components-testing/**
-alwaysApply: false
+name: components-testing
+description: ProtocolDeck component testing environment using built packages with Playwright visual snapshots in components-testing/. Use when working with component integration tests, package linking, or visual snapshot testing.
 ---
 
 # Components Testing — ProtocolDeck Component Testing Environment
@@ -28,49 +27,49 @@ Workflow: `pnpm install` → build packages as `.tgz` → extract to `pack/` →
 
 ## Project Structure
 
-```
+```markdown
 components-testing/
-├── Makefile                    # Build and setup automation
-├── package.json               # Dependencies (local packages NOT listed)
-├── pnpm-lock.yaml             # Lock file (unaffected by local links)
-├── playwright.config.ts       # Playwright test configuration
-├── vite.config.mts            # Vite configuration
-├── index.html                 # HTML entry point
-├── pack/                      # Gitignored .tgz packages
+├── Makefile # Build and setup automation
+├── package.json # Dependencies (local packages NOT listed)
+├── pnpm-lock.yaml # Lock file (unaffected by local links)
+├── playwright.config.ts # Playwright test configuration
+├── vite.config.mts # Vite configuration
+├── index.html # HTML entry point
+├── pack/ # Gitignored .tgz packages
 ├── src/
-│   ├── main.tsx               # Main application with ProtocolDeck test
-│   ├── styles.css             # Base styles
-│   └── StackerAnalysis.json   # Protocol analysis test data
+│ ├── main.tsx # Main application with ProtocolDeck test
+│ ├── styles.css # Base styles
+│ └── StackerAnalysis.json # Protocol analysis test data
 └── tests/
-    ├── protocolDeck.spec.ts   # Playwright visual tests
-    └── __screenshots__/       # Baseline screenshots (committed)
+├── protocolDeck.spec.ts # Playwright visual tests
+└── **screenshots**/ # Baseline screenshots (committed)
 ```
 
 ## Makefile Targets
 
 ### Setup
 
-| Target | Description |
-| --- | --- |
-| `make setup` | Complete setup: pnpm install, build packages, link them |
-| `make install-local-packages` | Rebuild and relink local packages only |
-| `make teardown` | Remove `pack/` and `node_modules` |
-| `make clean-local-packages` | Remove local packages only (keeps node_modules) |
+| Target                        | Description                                             |
+| ----------------------------- | ------------------------------------------------------- |
+| `make setup`                  | Complete setup: pnpm install, build packages, link them |
+| `make install-local-packages` | Rebuild and relink local packages only                  |
+| `make teardown`               | Remove `pack/` and `node_modules`                       |
+| `make clean-local-packages`   | Remove local packages only (keeps node_modules)         |
 
 ### Development
 
-| Target | Description |
-| --- | --- |
-| `make dev` | Start Vite dev server (localhost:5173) |
-| `make build` | Build for production |
-| `make preview` | Preview production build |
+| Target         | Description                            |
+| -------------- | -------------------------------------- |
+| `make dev`     | Start Vite dev server (localhost:5173) |
+| `make build`   | Build for production                   |
+| `make preview` | Preview production build               |
 
 ### Testing
 
-| Target | Description |
-| --- | --- |
-| `make test-setup` | Install Playwright browsers (one-time) |
-| `make test` | Run Playwright tests with current snapshots |
+| Target                       | Description                                       |
+| ---------------------------- | ------------------------------------------------- |
+| `make test-setup`            | Install Playwright browsers (one-time)            |
+| `make test`                  | Run Playwright tests with current snapshots       |
 | `make test-update-snapshots` | Update visual snapshots after intentional changes |
 
 ## Quick Start
diff --git a/.cursor/skills/css-modules/SKILL.md b/.cursor/skills/css-modules/SKILL.md
@@ -1,7 +1,6 @@
 ---
-description: CSS Modules file conventions, stylelint rules, and patterns
-globs: '**/*.module.css'
-alwaysApply: false
+name: css-modules
+description: CSS Modules conventions, Stylelint rules, design tokens (spacing, colors, typography, border-radius), and patterns for the Opentrons monorepo. Use when working with .module.css files or styling React components.
 ---
 
 # CSS Modules — Opentrons Conventions
@@ -10,12 +9,12 @@ alwaysApply: false
 
 File names are **lowercase**, no separators, suffixed with `.module.css`, and match the component name:
 
-```text
+```markdown
 ComponentName/
 ├── index.tsx
 ├── componentname.module.css
-└── __tests__/
-    └── ComponentName.test.tsx
+└── **tests**/
+└── ComponentName.test.tsx
 ```
 
 Examples: `navbar.module.css`, `labwarebutton.module.css`, `textareafield.module.css`
@@ -28,15 +27,22 @@ Use a `component_element` or `element_modifier` structure:
 
 ```css
 /* Base classes */
-.button { }
-.slider_container { }
-.crumb_link { }
+.button {
+}
+.slider_container {
+}
+.crumb_link {
+}
 
 /* State/modifier variants */
-.button_active { }
-.textarea_error { }
-.title_text_center { }
-.crumb_link_inactive { }
+.button_active {
+}
+.textarea_error {
+}
+.title_text_center {
+}
+.crumb_link_inactive {
+}
 ```
 
 ## Importing in Components
@@ -55,6 +61,7 @@ Use [clsx](https://github.com/lukeed/clsx) for combining or conditionally applyi
 
 ```tsx
 import clsx from 'clsx'
+
 import styles from './componentname.module.css'
 
 export function MyButton({ isActive, isError }: Props): JSX.Element {
@@ -72,25 +79,25 @@ All tokens are defined in `components/src/styles/global.css`. **Always use these
 
 ### Spacing
 
-| Variable | Value |
-| -------- | ----- |
-| `--spacing-2` | 0.125rem (2px) |
-| `--spacing-4` | 0.25rem (4px) |
-| `--spacing-6` | 0.375rem (6px) |
-| `--spacing-8` | 0.5rem (8px) |
-| `--spacing-10` | 0.625rem (10px) |
-| `--spacing-12` | 0.75rem (12px) |
-| `--spacing-16` | 1rem (16px) |
-| `--spacing-20` | 1.25rem (20px) |
-| `--spacing-24` | 1.5rem (24px) |
-| `--spacing-32` | 2rem (32px) |
-| `--spacing-40` | 2.5rem (40px) |
-| `--spacing-44` | 2.75rem (44px) |
-| `--spacing-48` | 3rem (48px) |
-| `--spacing-60` | 3.75rem (60px) |
-| `--spacing-68` | 4.25rem (68px) |
-| `--spacing-80` | 5rem (80px) |
-| `--spacing-120` | 7.5rem (120px) |
+| Variable        | Value           |
+| --------------- | --------------- |
+| `--spacing-2`   | 0.125rem (2px)  |
+| `--spacing-4`   | 0.25rem (4px)   |
+| `--spacing-6`   | 0.375rem (6px)  |
+| `--spacing-8`   | 0.5rem (8px)    |
+| `--spacing-10`  | 0.625rem (10px) |
+| `--spacing-12`  | 0.75rem (12px)  |
+| `--spacing-16`  | 1rem (16px)     |
+| `--spacing-20`  | 1.25rem (20px)  |
+| `--spacing-24`  | 1.5rem (24px)   |
+| `--spacing-32`  | 2rem (32px)     |
+| `--spacing-40`  | 2.5rem (40px)   |
+| `--spacing-44`  | 2.75rem (44px)  |
+| `--spacing-48`  | 3rem (48px)     |
+| `--spacing-60`  | 3.75rem (60px)  |
+| `--spacing-68`  | 4.25rem (68px)  |
+| `--spacing-80`  | 5rem (80px)     |
+| `--spacing-120` | 7.5rem (120px)  |
 
 ### Colors
 
@@ -128,16 +135,16 @@ All tokens are defined in `components/src/styles/global.css`. **Always use these
 
 ## Where to Use Tokens vs Explicit Values
 
-| Property | Use token? | Example |
-| -------- | ---------- | ------- |
-| `color`, `background-color`, `border-color` | **Yes** | `var(--blue-50)` |
-| `padding`, `margin`, `gap` | **Yes** | `var(--spacing-16)` |
-| `border-radius` | **Yes** | `var(--border-radius-8)` |
-| `font-size` | **Yes** | `var(--font-size-p)` |
-| `font-weight` | **Yes** | `var(--font-weight-semi-bold)` |
-| `line-height` | **Yes** | `var(--line-height-20)` |
-| `width`, `height`, `max-width`, `min-height` | **No** — use explicit `rem` | `15rem`, `100vh` |
-| `box-shadow` | **No** — use `px` | `0 0 0 2px var(--blue-50)` |
+| Property                                     | Use token?                  | Example                        |
+| -------------------------------------------- | --------------------------- | ------------------------------ |
+| `color`, `background-color`, `border-color`  | **Yes**                     | `var(--blue-50)`               |
+| `padding`, `margin`, `gap`                   | **Yes**                     | `var(--spacing-16)`            |
+| `border-radius`                              | **Yes**                     | `var(--border-radius-8)`       |
+| `font-size`                                  | **Yes**                     | `var(--font-size-p)`           |
+| `font-weight`                                | **Yes**                     | `var(--font-weight-semi-bold)` |
+| `line-height`                                | **Yes**                     | `var(--line-height-20)`        |
+| `width`, `height`, `max-width`, `min-height` | **No** — use explicit `rem` | `15rem`, `100vh`               |
+| `box-shadow`                                 | **No** — use `px`           | `0 0 0 2px var(--blue-50)`     |
 
 ## Unit Rules
 
diff --git a/.cursor/skills/e2e-testing/SKILL.md b/.cursor/skills/e2e-testing/SKILL.md
@@ -1,7 +1,6 @@
 ---
-description: E2E testing conventions for Protocol Designer and Labware Library using Playwright + pytest
-globs: e2e-testing/**
-alwaysApply: false
+name: e2e-testing
+description: E2E testing conventions for Protocol Designer and Labware Library using Playwright + pytest in e2e-testing/. Use when writing, running, or modifying end-to-end tests, page objects, or Playwright tests.
 ---
 
 # E2E Testing Instructions
@@ -119,36 +118,27 @@ Tests run against different environments via `TEST_ENV`:
 
 ### conftest.py Fixtures
 
-| Fixture | Scope | Purpose |
-| --- | --- | --- |
-| `pd_base_url` | session | Resolves PD URL; starts local preview server when `TEST_ENV=local` |
-| `ll_base_url` | session | Resolves LL URL; starts local preview server when `TEST_ENV=local` |
-| `page` | function | Creates a Playwright page, navigates to the correct app URL based on test markers, saves video |
-| `browser_context_args` | session | Viewport 1280x720, video recording |
-| `browser_type_launch_args` | session | Headless/headed, slow_mo |
-| `eyes` | function | Applitools Eyes session (or None) |
-| `eyes_singleton` | session | Shared Applitools Eyes instance |
+| Fixture                    | Scope    | Purpose                                                                                        |
+| -------------------------- | -------- | ---------------------------------------------------------------------------------------------- |
+| `pd_base_url`              | session  | Resolves PD URL; starts local preview server when `TEST_ENV=local`                             |
+| `ll_base_url`              | session  | Resolves LL URL; starts local preview server when `TEST_ENV=local`                             |
+| `page`                     | function | Creates a Playwright page, navigates to the correct app URL based on test markers, saves video |
+| `browser_context_args`     | session  | Viewport 1280x720, video recording                                                             |
+| `browser_type_launch_args` | session  | Headless/headed, slow_mo                                                                       |
+| `eyes`                     | function | Applitools Eyes session (or None)                                                              |
+| `eyes_singleton`           | session  | Shared Applitools Eyes instance                                                                |
 
 ### Key Environment Variables
 
-| Variable | Default | Notes |
-| --- | --- | --- |
-| `TEST_ENV` | `local` | `local`, `staging`, `prod`, `sandbox` |
-| `HEADLESS` | (unset) | `true` / `false`; overrides default |
-| `SKIP_SERVER_START` | `false` | Skip automatic server build+serve |
-| `PD_SERVER_URL` | auto | Override PD URL |
-| `LL_SERVER_URL` | auto | Override LL URL |
-| `LL_SERVER_PORT` | `4176` | Preferred port for LL local server |
-| `APPLITOOLS_API_KEY` | (unset) | Enable Applitools visual checks |
-
-## Key Files
-
-- **`conftest.py`** — Fixtures, server lifecycle, video recording, Applitools batch setup
-- **`pytest.ini`** — Markers (`pdE2E`, `llE2E`, `slow`, `unit`, `integration`), addopts, timeout (300 s)
-- **`pyproject.toml`** — Dependencies (`playwright>=1.55`, `eyes-playwright>=6.4`), ruff (line-length 120, py312), mypy (strict for `automation/`, relaxed for `tests/`)
-- **`eyes.py`** — `Eyes` wrapper class, `eyes` + `eyes_singleton` fixtures
-- **`utility.py`** — `troubleshoot_and_pause` decorator, `_import_protocol_and_open_editor`, `create_new_protocol_from_landing_page`
-- **`run_many_tests.py`** — Local "CI" runner: format, lint, typecheck with auto-fix
+| Variable             | Default | Notes                                 |
+| -------------------- | ------- | ------------------------------------- |
+| `TEST_ENV`           | `local` | `local`, `staging`, `prod`, `sandbox` |
+| `HEADLESS`           | (unset) | `true` / `false`; overrides default   |
+| `SKIP_SERVER_START`  | `false` | Skip automatic server build+serve     |
+| `PD_SERVER_URL`      | auto    | Override PD URL                       |
+| `LL_SERVER_URL`      | auto    | Override LL URL                       |
+| `LL_SERVER_PORT`     | `4176`  | Preferred port for LL local server    |
+| `APPLITOOLS_API_KEY` | (unset) | Enable Applitools visual checks       |
 
 ## Development Commands
 
diff --git a/.cursor/skills/locize-sync/SKILL.md b/.cursor/skills/locize-sync/SKILL.md
@@ -1,10 +1,6 @@
 ---
-description: Locize i18n synchronization workflow for the Opentrons monorepo
-globs:
-  - scripts/locize_sync.py
-  - app/src/assets/localization/**
-  - components/src/assets/localization/**
-alwaysApply: false
+name: locize-sync
+description: Locize i18n synchronization workflow for pushing and downloading translations in the Opentrons monorepo. Use when working with locize_sync.py, localization files in app/src/assets/localization/ or components/src/assets/localization/, or syncing translations.
 ---
 
 # Locize Synchronization Instructions
diff --git a/.cursor/skills/opentrons-typescript/SKILL.md b/.cursor/skills/opentrons-typescript/SKILL.md
@@ -1,6 +1,8 @@
 ---
-alwaysApply: false
+name: opentrons-typescript
+description: TypeScript conventions, React patterns, testing, styling, and import rules for the Opentrons monorepo JS/TS packages. Use when working with TypeScript or React files in app/, components/, shared-data/, step-generation/, protocol-designer/, opentrons-ai-client/, or other JS/TS packages.
 ---
+
 # Opentrons Monorepo — TypeScript Conventions
 
 Node.js, Yarn, Python setup, teardown, and troubleshooting are in the always-apply `monorepo-setup` rule.
@@ -11,35 +13,35 @@ Yarn workspaces monorepo with 14 TypeScript packages. No Lerna/Nx/Turbo — uses
 
 ### Packages
 
-| Package | Directory | Type |
-| ------- | --------- | ---- |
-| `@opentrons/app` | `app/` | React app |
-| `@opentrons/app-shell` | `app-shell/` | Electron shell |
-| `@opentrons/app-shell-odd` | `app-shell-odd/` | Electron shell (ODD) |
-| `@opentrons/components` | `components/` | React UI components library |
-| `@opentrons/api-client` | `api-client/` | Pure TS library |
-| `@opentrons/react-api-client` | `react-api-client/` | React hooks library |
-| `@opentrons/discovery-client` | `discovery-client/` | Pure TS (Node) |
-| `@opentrons/shared-data` | `shared-data/` | Pure TS/JS data library |
-| `@opentrons/step-generation` | `step-generation/` | Pure TS library |
-| `@opentrons/labware-library` | `labware-library/` | React app |
-| `@opentrons/labware-designer` | `labware-designer/` | React app |
-| `opentrons-ai-client` | `opentrons-ai-client/` | React app |
-| `protocol-designer` | `protocol-designer/` | React app |
-| `@opentrons/usb-bridge-client` | `usb-bridge/node-client/` | Pure TS (Node) |
+| Package                        | Directory                 | Type                        |
+| ------------------------------ | ------------------------- | --------------------------- |
+| `@opentrons/app`               | `app/`                    | React app                   |
+| `@opentrons/app-shell`         | `app-shell/`              | Electron shell              |
+| `@opentrons/app-shell-odd`     | `app-shell-odd/`          | Electron shell (ODD)        |
+| `@opentrons/components`        | `components/`             | React UI components library |
+| `@opentrons/api-client`        | `api-client/`             | Pure TS library             |
+| `@opentrons/react-api-client`  | `react-api-client/`       | React hooks library         |
+| `@opentrons/discovery-client`  | `discovery-client/`       | Pure TS (Node)              |
+| `@opentrons/shared-data`       | `shared-data/`            | Pure TS/JS data library     |
+| `@opentrons/step-generation`   | `step-generation/`        | Pure TS library             |
+| `@opentrons/labware-library`   | `labware-library/`        | React app                   |
+| `@opentrons/labware-designer`  | `labware-designer/`       | React app                   |
+| `opentrons-ai-client`          | `opentrons-ai-client/`    | React app                   |
+| `protocol-designer`            | `protocol-designer/`      | React app                   |
+| `@opentrons/usb-bridge-client` | `usb-bridge/node-client/` | Pure TS (Node)              |
 
 ### Dependency Graph
 
 `shared-data` is the foundation. Nothing should import "up" the tree:
 
-```md
+```markdown
 shared-data
-  ├── step-generation
-  ├── components
-  ├── api-client → react-api-client
-  └── discovery-client
-       ↓
-  app, protocol-designer, labware-library, opentrons-ai-client (leaf apps)
+├── step-generation
+├── components
+├── api-client → react-api-client
+└── discovery-client
+↓
+app, protocol-designer, labware-library, opentrons-ai-client (leaf apps)
 ```
 
 ## TypeScript Configuration
@@ -83,6 +85,7 @@ Use the `@opentrons/` scope. These resolve to source via Vite aliases in dev/tes
 ```typescript
 import { Flex, SPACING } from '@opentrons/components'
 import { getPipetteSpecsV2 } from '@opentrons/shared-data'
+
 import type { PipetteName } from '@opentrons/shared-data'
 ```
 
@@ -98,11 +101,10 @@ Each app has a path alias (configured in tsconfig + Vite):
 // Good — absolute import within app
 import { useRobot } from '/app/resources/robots'
 
-// Acceptable — relative for nearby files in the same feature
-import { utils } from './utils'
-
 // Bad — deep relative paths across features
 import { useRobot } from '../../../resources/robots'
+// Acceptable — relative for nearby files in the same feature
+import { utils } from './utils'
 ```
 
 ### No Default Exports
@@ -115,10 +117,10 @@ Import individual functions only:
 
 ```typescript
 // Good
-import mapValues from 'lodash/mapValues'
 
 // Bad — imports entire library
 import { mapValues } from 'lodash'
+import mapValues from 'lodash/mapValues'
 ```
 
 ### Type Imports
@@ -165,7 +167,14 @@ The `app` package separates Desktop and ODD (On-Device Display) UIs. ESLint rule
 Use primitives from the shared component library for layout and common UI:
 
 ```typescript
-import { Flex, StyledText, Icon, SPACING, COLORS, DIRECTION_COLUMN } from '@opentrons/components'
+import {
+  COLORS,
+  DIRECTION_COLUMN,
+  Flex,
+  Icon,
+  SPACING,
+  StyledText,
+} from '@opentrons/components'
 ```
 
 ### Hooks
@@ -224,11 +233,11 @@ width: 15rem;
 
 ### Test File Structure
 
-```text
+```markdown
 FeatureOrComponent/
 ├── index.tsx (or module.ts)
-└── __tests__/
-    └── FeatureName.test.tsx
+└── **tests**/
+└── FeatureName.test.tsx
 ```
 
 ### renderWithProviders
@@ -274,30 +283,30 @@ describe('MyComponent', () => {
 
 Each package has a `Makefile` with some or all of:
 
-| Target | Description |
-| ------ | ----------- |
-| `make dev` | Start Vite dev server |
-| `make build` | Production build |
-| `make clean` | Remove build output |
-| `make test` | Run tests (delegates to root) |
-| `make test-cov` | Run tests with coverage |
+| Target          | Description                   |
+| --------------- | ----------------------------- |
+| `make dev`      | Start Vite dev server         |
+| `make build`    | Production build              |
+| `make clean`    | Remove build output           |
+| `make test`     | Run tests (delegates to root) |
+| `make test-cov` | Run tests with coverage       |
 
 ### Root Makefile (run from monorepo root)
 
-| Target | Description |
-| ------ | ----------- |
-| `make setup-js` | Install all JS deps (`yarn`) |
-| `make test-js` | Run ALL JS tests |
-| `make test-js-<project>` | Run tests for one project (e.g., `make test-js-protocol-designer`) |
-| `make lint-js` | ESLint + Prettier check |
-| `make lint-js-eslint` | ESLint only |
-| `make lint-js-prettier` | Prettier only |
-| `make lint-css` | Stylelint all CSS |
-| `make format-js` | Auto-format with Prettier |
-| `make format-css` | Auto-fix CSS with Stylelint |
-| `make check-js` / `make build-ts` | TypeScript type-check (`tsc --build`) |
-| `make clean-ts` | Clean TS build output |
-| `make circular-dependencies-js` | Check circular imports (madge) |
+| Target                            | Description                                                        |
+| --------------------------------- | ------------------------------------------------------------------ |
+| `make setup-js`                   | Install all JS deps (`yarn`)                                       |
+| `make test-js`                    | Run ALL JS tests                                                   |
+| `make test-js-<project>`          | Run tests for one project (e.g., `make test-js-protocol-designer`) |
+| `make lint-js`                    | ESLint + Prettier check                                            |
+| `make lint-js-eslint`             | ESLint only                                                        |
+| `make lint-js-prettier`           | Prettier only                                                      |
+| `make lint-css`                   | Stylelint all CSS                                                  |
+| `make format-js`                  | Auto-format with Prettier                                          |
+| `make format-css`                 | Auto-fix CSS with Stylelint                                        |
+| `make check-js` / `make build-ts` | TypeScript type-check (`tsc --build`)                              |
+| `make clean-ts`                   | Clean TS build output                                              |
+| `make circular-dependencies-js`   | Check circular imports (madge)                                     |
 
 ### Running Tests Directly
 
diff --git a/.cursor/skills/protocol-designer/SKILL.md b/.cursor/skills/protocol-designer/SKILL.md
@@ -1,16 +1,15 @@
 ---
-description: Protocol Designer (PD) application-specific architecture, domain concepts, and dev workflow
-globs: protocol-designer/**
-alwaysApply: false
+name: protocol-designer
+description: Protocol Designer (PD) application architecture, Redux slices, step/timeline system, domain concepts, and dev workflow. Use when working with files in protocol-designer/ or discussing PD features, steps, timelines, or protocol design.
 ---
 
 # Protocol Designer — Application-Specific Conventions
 
-General TypeScript, React, styling, testing, import, and tooling conventions are in the `opentrons-typescript` rule. This file covers only what is unique to the `protocol-designer` package.
+General TypeScript, React, styling, testing, import, and tooling conventions are in the `opentrons-typescript` skill. This file covers only what is unique to the `protocol-designer` package.
 
 ## Project Overview
 
-Protocol Designer (PD) is a React + Redux + React Router + TypeScript web app for designing Opentrons liquid-handling protocols. It depends on `@opentrons/components`, `@opentrons/shared-data`, and `@opentrons/step-generation`.  It follows an atomic design system.
+Protocol Designer (PD) is a React + Redux + React Router + TypeScript web app for designing Opentrons liquid-handling protocols. It depends on `@opentrons/components`, `@opentrons/shared-data`, and `@opentrons/step-generation`. It follows an atomic design system.
 
 ## Redux Architecture
 
@@ -20,19 +19,19 @@ PD uses **Redux** (legacy `createStore`) with **redux-thunk** and **reselect**.
 
 Each slice directory contains `reducers/`, `actions/`, `selectors/`, and `types.ts`:
 
-| Slice | Key | Purpose |
-| ----- | --- | ------- |
-| `analytics` | `analytics` | Event tracking |
-| `dismiss` | `dismiss` | Dismissible UI elements |
-| `feature-flags` | `featureFlags` | Feature flags (`OT_PD_*` env vars) |
-| `file-data` | `fileData` | Protocol file data and export |
-| `labware-ingred` | `labwareIngred` | Labware, ingredients, deck state |
-| `load-file` | `loadFile` | File loading/parsing |
-| `navigation` | `navigation` | Navigation state |
-| `step-forms` | `stepForms` | Saved step forms, pipettes, modules, labware entities |
-| `tutorial` | `tutorial` | Tutorial/hint state |
-| `ui` | `ui` | UI state (steps, labware, wells) |
-| `well-selection` | `wellSelection` | Well selection state |
+| Slice            | Key             | Purpose                                               |
+| ---------------- | --------------- | ----------------------------------------------------- |
+| `analytics`      | `analytics`     | Event tracking                                        |
+| `dismiss`        | `dismiss`       | Dismissible UI elements                               |
+| `feature-flags`  | `featureFlags`  | Feature flags (`OT_PD_*` env vars)                    |
+| `file-data`      | `fileData`      | Protocol file data and export                         |
+| `labware-ingred` | `labwareIngred` | Labware, ingredients, deck state                      |
+| `load-file`      | `loadFile`      | File loading/parsing                                  |
+| `navigation`     | `navigation`    | Navigation state                                      |
+| `step-forms`     | `stepForms`     | Saved step forms, pipettes, modules, labware entities |
+| `tutorial`       | `tutorial`      | Tutorial/hint state                                   |
+| `ui`             | `ui`            | UI state (steps, labware, wells)                      |
+| `well-selection` | `wellSelection` | Well selection state                                  |
 
 ### Middleware
 
@@ -46,6 +45,7 @@ Use **reselect** `createSelector` for all derived state. Per-slice selectors go
 
 ```typescript
 import { createSelector } from 'reselect'
+
 export const getLabwareNicknamesById = createSelector(
   getLabwareEntities,
   labwareEntities => mapValues(labwareEntities, e => e.nickname)
@@ -56,6 +56,7 @@ export const getLabwareNicknamesById = createSelector(
 
 ```typescript
 import type { ThunkAction } from '/protocol-designer/types'
+
 export const myThunk = (): ThunkAction<any> => (dispatch, getState) => {
   const state = getState()
   dispatch({ type: 'MY_ACTION', payload: someSelector(state) })
@@ -107,6 +108,7 @@ The `/protocol-designer/` path alias maps to `src/`. Use it for imports across f
 
 ```typescript
 import { getFileMetadata } from '/protocol-designer/file-data/selectors'
+
 import type { BaseState } from '/protocol-designer/types'
 ```
 
@@ -140,16 +142,16 @@ import { renderWithProviders } from '/protocol-designer/__testing-utils__'
 
 Run from the `protocol-designer/` directory:
 
-| Target | Description |
-| ------ | ----------- |
-| `make dev` | Start Vite dev server (port 5178) |
-| `make build` | Production build (8GB heap) |
-| `make serve` | Build then preview production assets |
-| `make clean` | Remove `dist/` |
-| `make test` | Run PD tests (delegates to root `make test-js-protocol-designer`) |
-| `make test-cov` | Tests with coverage |
-| `make bundle-analyzer` | Analyze production bundle size |
-| `make benchmarks` | Run performance benchmarks (output in `benchmarks/output/`) |
+| Target                 | Description                                                       |
+| ---------------------- | ----------------------------------------------------------------- |
+| `make dev`             | Start Vite dev server (port 5178)                                 |
+| `make build`           | Production build (8GB heap)                                       |
+| `make serve`           | Build then preview production assets                              |
+| `make clean`           | Remove `dist/`                                                    |
+| `make test`            | Run PD tests (delegates to root `make test-js-protocol-designer`) |
+| `make test-cov`        | Tests with coverage                                               |
+| `make bundle-analyzer` | Analyze production bundle size                                    |
+| `make benchmarks`      | Run performance benchmarks (output in `benchmarks/output/`)       |
 
 ```bash
 # Run a specific test file
diff --git a/.cursor/skills/react-component-creation/SKILL.md b/.cursor/skills/react-component-creation/SKILL.md
@@ -1,14 +1,11 @@
 ---
-description: Component creation checklist and ai-client-specific patterns for React .tsx files
-globs:
-  - opentrons-ai-client/src/**/*.tsx
-  - protocol-designer/src/**/*.tsx
-alwaysApply: false
+name: react-component-creation
+description: Component creation checklist and ai-client-specific patterns for React .tsx files in opentrons-ai-client/ and protocol-designer/. Use when creating new React components in these packages.
 ---
 
 # React Component Creation Checklist
 
-General TypeScript, React, styling, testing, and import conventions are in the `opentrons-typescript` and `css-modules` rules. PD-specific architecture is in the `protocol-designer` rule. This file covers the **component creation workflow** and **opentrons-ai-client specifics**.
+General TypeScript, React, styling, testing, and import conventions are in the `opentrons-typescript` skill. PD-specific architecture is in the `protocol-designer` skill. CSS Modules details are in the `css-modules` skill. This file covers the **component creation workflow** and **opentrons-ai-client specifics**.
 
 ## Before Creating a New Component
 
@@ -35,8 +32,9 @@ ComponentName/
 The ai-client uses `/ai-client/` as its path alias (mapped to `opentrons-ai-client/src/`):
 
 ```typescript
-import type { ChatData } from '/ai-client/resources/types'
 import { AttachedFileItem } from '/ai-client/atoms/AttachedFileItem'
+
+import type { ChatData } from '/ai-client/resources/types'
 ```
 
 ### Testing
diff --git a/.cursor/skills/robot-python-projects/SKILL.md b/.cursor/skills/robot-python-projects/SKILL.md
@@ -1,46 +1,24 @@
 ---
-description: Guidelines for working with the robot Python projects
-globs:
-  - api/**/*.py
-  - robot-server/**/*.py
-  - hardware/**/*.py
-  - auth-server/**/*.py
-  - shared-data/python/**/*.py
-  - shared-data/python_tests/**/*.py
-  - server-utils/**/*.py
-  - system-server/**/*.py
-  - update-server/**/*.py
-  - usb-bridge/**/*.py
-  - g-code-testing/**/*.py
-  - api/pyproject.toml
-  - robot-server/pyproject.toml
-  - hardware/pyproject.toml
-  - auth-server/pyproject.toml
-  - shared-data/pyproject.toml
-  - server-utils/pyproject.toml
-  - system-server/pyproject.toml
-  - update-server/pyproject.toml
-  - usb-bridge/pyproject.toml
-  - g-code-testing/pyproject.toml
-alwaysApply: false
+name: robot-python-projects
+description: Guidelines for robot Python projects — api/, robot-server/, hardware/, auth-server/, shared-data/, server-utils/, system-server/, update-server/, usb-bridge/, g-code-testing/. Use when working with Python files in these directories or their pyproject.toml files.
 ---
 
 # Robot Python Projects
 
 The following directories contain the robot Python projects — packages that run on or support Opentrons robots:
 
-| Project | Directory | Description |
-| --- | --- | --- |
-| `opentrons` | `api/` | Core Opentrons Python API for protocol execution |
-| `robot-server` | `robot-server/` | HTTP API server that runs on the robot |
-| `opentrons-hardware` | `hardware/` | Low-level hardware control and CAN bus communication |
-| `auth-server` | `auth-server/` | Authentication server for Flex |
-| `opentrons-shared-data` | `shared-data/` | Shared data definitions (labware, pipettes, modules) |
-| `server-utils` | `server-utils/` | Common utilities for Python servers |
-| `system-server` | `system-server/` | System-level server for robot management |
-| `otupdate` | `update-server/` | Server for software and firmware updates |
-| `ot3usb` | `usb-bridge/` | USB bridge daemon for Flex |
-| `g-code-testing` | `g-code-testing/` | G-code testing and emulation tools |
+| Project                 | Directory         | Description                                          |
+| ----------------------- | ----------------- | ---------------------------------------------------- |
+| `opentrons`             | `api/`            | Core Opentrons Python API for protocol execution     |
+| `robot-server`          | `robot-server/`   | HTTP API server that runs on the robot               |
+| `opentrons-hardware`    | `hardware/`       | Low-level hardware control and CAN bus communication |
+| `auth-server`           | `auth-server/`    | Authentication server for Flex                       |
+| `opentrons-shared-data` | `shared-data/`    | Shared data definitions (labware, pipettes, modules) |
+| `server-utils`          | `server-utils/`   | Common utilities for Python servers                  |
+| `system-server`         | `system-server/`  | System-level server for robot management             |
+| `otupdate`              | `update-server/`  | Server for software and firmware updates             |
+| `ot3usb`                | `usb-bridge/`     | USB bridge daemon for Flex                           |
+| `g-code-testing`        | `g-code-testing/` | G-code testing and emulation tools                   |
 
 ## Common Patterns
 
diff --git a/.cursor/skills/static-deploy/SKILL.md b/.cursor/skills/static-deploy/SKILL.md
@@ -1,7 +1,6 @@
 ---
-description: Conventions for static deploy automation Python CLIs
-globs: scripts/static-deploy/**
-alwaysApply: false
+name: static-deploy
+description: Conventions for static deploy automation Python CLIs in scripts/static-deploy/. Use when working with deployment scripts, AWS S3/CloudFront automation, or Python CLIs in the static-deploy directory.
 ---
 
 # Static Deploy — Python CLI Conventions
@@ -37,6 +36,7 @@ alwaysApply: false
 ### Environment Parity
 
 Same code path runs locally and in CI. Only entry points differ:
+
 - **Local**: dev sets flags manually (`--aws-profile`, etc.)
 - **CI**: wrapper or Make target builds the same args from CI env
 
@@ -45,6 +45,7 @@ Configuration should be static and deterministic — avoid runtime environment d
 ### Rich Console UX
 
 Use `rich.console.Console` for all human output:
+
 - `style="red"` for errors
 - `style="yellow"` for warnings
 - `style="green"` for success
PATCH

echo "Gold patch applied."
