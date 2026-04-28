#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dify

# Idempotency guard
if grep -qF "- Backend QA gate requires passing `make lint`, `make type-check`, and `uv run -" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -4,84 +4,51 @@
 
 Dify is an open-source platform for developing LLM applications with an intuitive interface combining agentic AI workflows, RAG pipelines, agent capabilities, and model management.
 
-The codebase consists of:
+The codebase is split into:
 
-- **Backend API** (`/api`): Python Flask application with Domain-Driven Design architecture
-- **Frontend Web** (`/web`): Next.js 15 application with TypeScript and React 19
+- **Backend API** (`/api`): Python Flask application organized with Domain-Driven Design
+- **Frontend Web** (`/web`): Next.js 15 application using TypeScript and React 19
 - **Docker deployment** (`/docker`): Containerized deployment configurations
 
-## Development Commands
+## Backend Workflow
 
-### Backend (API)
+- Run backend CLI commands through `uv run --project api <command>`.
 
-All Python commands must be prefixed with `uv run --project api`:
+- Backend QA gate requires passing `make lint`, `make type-check`, and `uv run --project api --dev dev/pytest/pytest_unit_tests.sh` before review.
 
-```bash
-# Start development servers
-./dev/start-api                   # Start API server
-./dev/start-worker                # Start Celery worker
-
-# Run tests
-uv run --project api pytest      # Run all tests
-uv run --project api pytest tests/unit_tests/     # Unit tests only
-uv run --project api pytest tests/integration_tests/  # Integration tests
-
-# Code quality
-./dev/reformat                    # Run all formatters and linters
-uv run --project api ruff check --fix ./    # Fix linting issues
-uv run --project api ruff format ./         # Format code
-uv run --directory api basedpyright         # Type checking
-```
+- Use Makefile targets for linting and formatting; `make lint` and `make type-check` cover the required checks.
+
+- Integration tests are CI-only and are not expected to run in the local environment.
 
-### Frontend (Web)
+## Frontend Workflow
 
 ```bash
 cd web
-pnpm lint                         # Run ESLint
-pnpm lint:fix                     # Fix ESLint issues
-pnpm test                         # Run Jest tests
+pnpm lint
+pnpm lint:fix
+pnpm test
 ```
 
-## Testing Guidelines
-
-### Backend Testing
-
-- Use `pytest` for all backend tests
-- Write tests first (TDD approach)
-- Test structure: Arrange-Act-Assert
-
-## Code Style Requirements
-
-### Python
-
-- Use type hints for all functions and class attributes
-- No `Any` types unless absolutely necessary
-- Implement special methods (`__repr__`, `__str__`) appropriately
-
-### TypeScript/JavaScript
-
-- Strict TypeScript configuration
-- ESLint with Prettier integration
-- Avoid `any` type
+## Testing & Quality Practices
 
-## Important Notes
+- Follow TDD: red → green → refactor.
+- Use `pytest` for backend tests with Arrange-Act-Assert structure.
+- Enforce strong typing; avoid `Any` and prefer explicit type annotations.
+- Write self-documenting code; only add comments that explain intent.
 
-- **Environment Variables**: Always use UV for Python commands: `uv run --project api <command>`
-- **Comments**: Only write meaningful comments that explain "why", not "what"
-- **File Creation**: Always prefer editing existing files over creating new ones
-- **Documentation**: Don't create documentation files unless explicitly requested
-- **Code Quality**: Always run `./dev/reformat` before committing backend changes
+## Language Style
 
-## Common Development Tasks
+- **Python**: Keep type hints on functions and attributes, and implement relevant special methods (e.g., `__repr__`, `__str__`).
+- **TypeScript**: Use the strict config, lean on ESLint + Prettier workflows, and avoid `any` types.
 
-### Adding a New API Endpoint
+## General Practices
 
-1. Create controller in `/api/controllers/`
-1. Add service logic in `/api/services/`
-1. Update routes in controller's `__init__.py`
-1. Write tests in `/api/tests/`
+- Prefer editing existing files; add new documentation only when requested.
+- Inject dependencies through constructors and preserve clean architecture boundaries.
+- Handle errors with domain-specific exceptions at the correct layer.
 
-## Project-Specific Conventions
+## Project Conventions
 
-- All async tasks use Celery with Redis as broker
-- **Internationalization**: Frontend supports multiple languages with English (`web/i18n/en-US/`) as the source. All user-facing text must use i18n keys, no hardcoded strings. Edit corresponding module files in `en-US/` directory for translations.
+- Backend architecture adheres to DDD and Clean Architecture principles.
+- Async work runs through Celery with Redis as the broker.
+- Frontend user-facing strings must use `web/i18n/en-US/`; avoid hardcoded text.
PATCH

echo "Gold patch applied."
