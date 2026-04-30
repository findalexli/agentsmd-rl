#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openproject

# Idempotency guard
if grep -qF "See [`docker/dev/AGENTS.md`](docker/dev/AGENTS.md) for full Docker setup and com" "AGENTS.md" && grep -qF "- Follow [Ruby community style guide](https://github.com/bbatsov/ruby-style-guid" "app/AGENTS.md" && grep -qF "app/CLAUDE.md" "app/CLAUDE.md" && grep -qF "bundle exec i18n-tasks check-consistent-interpolations  # Check interpolation co" "config/AGENTS.md" && grep -qF "config/CLAUDE.md" "config/CLAUDE.md" && grep -qF "**CRITICAL**: `config/database.yml` must NOT exist when using Docker (rename or " "db/AGENTS.md" && grep -qF "db/CLAUDE.md" "db/CLAUDE.md" && grep -qF "bin/compose run                           # Start frontend in background, backen" "docker/dev/AGENTS.md" && grep -qF "docker/dev/CLAUDE.md" "docker/dev/CLAUDE.md" && grep -qF "- **New development**: Use Hotwire (Turbo + Stimulus) with server-rendered HTML" "frontend/AGENTS.md" && grep -qF "frontend/CLAUDE.md" "frontend/CLAUDE.md" && grep -qF "bin/compose rspec spec/models/user_spec.rb   # Run specific tests in backend-tes" "spec/AGENTS.md" && grep -qF "spec/CLAUDE.md" "spec/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -20,8 +20,6 @@
 - Node: `^22.21.0` (see `package.json` engines)
 - Bundler: Latest 2.x
 
-OpenProject supports two development setups: **Local** and **Docker**. Choose one based on your preference.
-
 ### Local Development Setup
 
 ```bash
@@ -34,59 +32,24 @@ bin/dev                          # Start all services (Rails, frontend, Good Job
 
 ### Docker Development Setup
 
-The Docker development environment uses configurations in `docker/dev/` and the `bin/compose` wrapper script.
-
-```bash
-# Initial setup (first time only)
-bin/compose setup                         # Installs backend and frontend dependencies
-
-# Starting services
-bin/compose start                         # Start backend and frontend in background
-bin/compose run                           # Start frontend in background, backend in foreground (for debugging with pry)
-
-# Running tests
-bin/compose rspec spec/models/user_spec.rb   # Run specific tests in backend-test container
-
-# Other operations
-bin/compose reset                         # Remove all containers and volumes (requires setup again)
-bin/compose <command>                     # Pass any docker-compose command directly
-```
-
-**Important Docker Notes:**
-- **CRITICAL**: `config/database.yml` must NOT exist when using Docker (rename or delete it)
-- Most developers use a local `docker-compose.override.yml` for custom port mappings and configurations
-- Copy `docker-compose.override.example.yml` to `docker-compose.override.yml` and customize as needed
-- Default ports: Backend at http://localhost:3000 (or 4200 for frontend dev server)
-- Services: `backend`, `frontend`, `worker`, `db`, `db-test`, `backend-test`, `cache`
-- Persisted volumes: `pgdata`, `bundle`, `npm`, `tmp`, `opdata` (data survives container restarts)
-- Docker build context: Uses Dockerfiles in `docker/dev/backend/` and `docker/dev/frontend/`
+See [`docker/dev/AGENTS.md`](docker/dev/AGENTS.md) for full Docker setup and commands.
 
 ## Project Structure
 
 ### Key Directories
-- `app/` - Rails application code
-  - `app/components/` - ViewComponent-based UI components (Ruby + ERB)
-  - `app/contracts/` - Validation and authorization contracts
-  - `app/controllers/` - Rails controllers
-  - `app/models/` - ActiveRecord models
-  - `app/services/` - Service objects (business logic)
-  - `app/workers/` - Background job workers
-- `config/` - Rails configuration, routes, locales
-- `db/` - Database migrations and seeds
-- `frontend/src/` - Frontend code
-  - `frontend/src/app/` - Legacy Angular modules/components
-  - `frontend/src/stimulus/` - Stimulus controllers
-  - `frontend/src/turbo/` - Turbo integration
-- `lib/` - Ruby libraries and extensions
-- `lookbook/` - ViewComponent previews (https://qa.openproject-edge.com/lookbook/)
-- `modules/` - OpenProject plugin modules
-- `spec/` - RSpec test suite
-  - `spec/features/` - System/feature tests (Capybara)
-  - `spec/models/` - Model unit tests
-  - `spec/requests/` - API/integration tests
-  - `spec/services/` - Service tests
+
+- `app/` — Rails application code
+- `config/` — Rails configuration, routes, locales
+- `db/` — Database migrations and seeds
+- `docker/dev/` — Docker development environment
+- `frontend/` — TypeScript/Angular/Stimulus frontend
+- `lib/` — Ruby libraries and extensions
+- `lookbook/` — ViewComponent previews (<https://qa.openproject-edge.com/lookbook/>)
+- `modules/` — OpenProject plugin modules
+- `spec/` — RSpec test suite
 
 ### Configuration Files
+
 - `.ruby-version` - Ruby version
 - `.rubocop.yml` - Ruby linting rules
 - `.erb_lint.yml` - ERB template linting
@@ -95,8 +58,6 @@ bin/compose <command>                     # Pass any docker-compose command dire
 - `package.json` / `frontend/package.json` - Node.js dependencies
 - `lefthook.yml` - Git hooks configuration
 
-## Building and Testing
-
 ### Linting (Run Before Committing)
 
 ```bash
@@ -114,125 +75,16 @@ erb_lint {files}
 bundle exec lefthook install
 ```
 
-### Running Tests
-
-```bash
-# Backend (RSpec) - prefer specific tests over running all
-bundle exec rspec spec/models/user_spec.rb              # Single file
-bundle exec rspec spec/models/user_spec.rb:42           # Single line
-bundle exec rspec spec/features                         # Directory
-bundle exec rake parallel:spec                          # Parallel execution
-
-# Frontend (Jasmine/Karma)
-cd frontend && npm test && cd ..
-```
-
-### Debugging CI Failures
-```bash
-./script/github_pr_errors | xargs bundle exec rspec    # Run failed tests from CI
-./script/bulk_run_rspec spec/path/to/flaky_spec.rb     # Run tests multiple times
-```
+## Commit Messages
 
-## Code Style Guidelines
-
-### Ruby
-- Follow [Ruby community style guide](https://github.com/bbatsov/ruby-style-guide)
-- Use service objects for complex business logic (return `ServiceResult`)
-- Use contracts for validation and authorization
-- Keep controllers thin, models focused
-- Document with [YARD](https://yardoc.org/)
-- Write RSpec tests for all new features
-
-### JavaScript/TypeScript
-- **New development**: Use Hotwire (Turbo + Stimulus) with server-rendered HTML
-- **Legacy code**: Follow ESLint rules
-- Prefer TypeScript over JavaScript
-- Use [Primer Design System](https://primer.style/product/) via ViewComponent
-
-### Templates
-- Use ERB for server-rendered views
-- Use ViewComponents for reusable UI (with Lookbook previews)
-- Lint with erb_lint before committing
-
-### Database Migrations
-- Follow Rails migration conventions
-- Migrations are "squashed" between major releases (see `docs/development/migrations/`)
-
-### Translations
-- UI strings must use translation keys (never hard-coded)
-- Source translations in `**/config/locales/en.yml` can be modified directly
-- Other translations managed via Crowdin
-
-### Commit Messages
 - First line: < 72 characters, then blank line, then detailed description
 - Reference work packages when applicable
 - Merge strategy: "Merge pull request" (not squash), except single-commit PRs can use "Rebase and merge"
 
-## Important Commands Reference
-
-### Local Development Commands
-
-```bash
-# Setup
-bin/setup              # Initial Rails setup
-bin/setup_dev          # Full dev environment setup
-
-# Database
-bundle exec rails g migration MigrationName  # Generate a migration
-bundle exec rails db:migrate                 # Run migrations
-bundle exec rails db:rollback                # Rollback last migration
-bundle exec rails db:seed                    # Seed sample data
-
-# Development
-bin/dev                                  # Start all services
-bundle exec rails console                # Rails console
-bundle exec rails routes                 # List routes
-
-# Testing
-bundle exec rspec                        # Run RSpec tests
-bundle exec rails parallel:spec          # Parallel tests
-cd frontend && npm test                  # Frontend tests
-
-# Linting
-bundle exec rubocop                      # Ruby linting
-cd frontend && npx eslint src/           # JS/TS linting
-erb_lint {files}                         # ERB linting
-```
-
-### Docker Development Commands
-
-```bash
-# Setup and lifecycle
-bin/compose setup                        # Setup Docker environment (first time)
-bin/compose start                        # Start all services in background
-bin/compose run                          # Start frontend in background, backend in foreground
-bin/compose reset                        # Remove all containers and volumes
-bin/compose stop                         # Stop all services
-bin/compose down                         # Stop and remove containers
-
-# Testing
-bin/compose rspec spec/models/user_spec.rb    # Run specific tests
-bin/compose exec backend bundle exec rspec    # Run tests directly in backend container
-
-# Development
-bin/compose exec backend bundle exec rails console   # Rails console
-bin/compose logs backend                 # View backend logs
-bin/compose logs -f backend              # Follow backend logs
-bin/compose ps                           # List running containers
-
-# Database
-bin/compose exec backend bundle exec rails db:migrate      # Run migrations
-bin/compose exec backend bundle exec rails db:seed         # Seed data
-
-# Direct docker-compose commands
-bin/compose up -d                        # Start services
-bin/compose restart backend              # Restart backend service
-```
-
 ## Additional Documentation
 
-- `docs/development/` - Development documentation
-- `docs/development/running-tests/` - Testing guide
-- `docs/development/code-review-guidelines/` - Code review standards
-- `CONTRIBUTING.md` - Contribution workflow
-- `.github/copilot-instructions.md` - Extended agent instructions with troubleshooting
+- `docs/development/` — Development documentation
+- `docs/development/running-tests/` — Testing guide
+- `docs/development/code-review-guidelines/` — Code review standards
+- `CONTRIBUTING.md` — Contribution workflow
+- `.github/copilot-instructions.md` — Extended agent instructions with troubleshooting
diff --git a/app/AGENTS.md b/app/AGENTS.md
@@ -0,0 +1,31 @@
+# App
+
+## Directory Structure
+
+- `app/components/` - ViewComponent-based UI components (Ruby + ERB)
+- `app/contracts/` - Validation and authorization contracts
+- `app/controllers/` - Rails controllers
+- `app/models/` - ActiveRecord models
+- `app/services/` - Service objects (business logic)
+- `app/workers/` - Background job workers
+
+## Code Style
+
+### Ruby
+
+- Follow [Ruby community style guide](https://github.com/bbatsov/ruby-style-guide)
+- Use service objects for complex business logic (return `ServiceResult`)
+- Use contracts for validation and authorization
+- Keep controllers thin, models focused
+- Document with [YARD](https://yardoc.org/)
+- Write RSpec tests for all new features
+
+### Templates
+
+- Use ERB for server-rendered views
+- Use ViewComponents for reusable UI (with Lookbook previews)
+- Lint with erb_lint before committing
+
+## Translations
+
+- UI strings must use translation keys (never hard-coded)
diff --git a/app/CLAUDE.md b/app/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/config/AGENTS.md b/config/AGENTS.md
@@ -0,0 +1,14 @@
+# Config
+
+## Translations
+
+- UI strings must use translation keys (never hard-coded)
+- Source translations in `**/config/locales/en.yml` can be modified directly
+- Other translations managed via Crowdin
+
+```bash
+bundle exec i18n-tasks missing                        # Show missing translation keys
+bundle exec i18n-tasks unused                         # Show unused translation keys
+bundle exec i18n-tasks normalize                      # Fix/normalize translation files
+bundle exec i18n-tasks check-consistent-interpolations  # Check interpolation consistency
+```
diff --git a/config/CLAUDE.md b/config/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/db/AGENTS.md b/db/AGENTS.md
@@ -0,0 +1,30 @@
+# Database
+
+## Code Style
+
+### Database Migrations
+
+- Follow Rails migration conventions
+- Migrations are "squashed" between major releases (see `docs/development/migrations/`)
+
+## Commands
+
+### Local
+
+```bash
+bundle exec rails g migration MigrationName  # Generate a migration
+bundle exec rails db:migrate                 # Run migrations
+bundle exec rails db:rollback                # Rollback last migration
+bundle exec rails db:seed                    # Seed sample data
+```
+
+### Docker
+
+```bash
+bin/compose exec backend bundle exec rails db:migrate      # Run migrations
+bin/compose exec backend bundle exec rails db:seed         # Seed data
+```
+
+## Important Note
+
+**CRITICAL**: `config/database.yml` must NOT exist when using Docker (rename or delete it)
diff --git a/db/CLAUDE.md b/db/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/docker/dev/AGENTS.md b/docker/dev/AGENTS.md
@@ -0,0 +1,61 @@
+# Docker Development
+
+The Docker development environment uses configurations in `docker/dev/` and the `bin/compose` wrapper script.
+
+## Setup
+
+```bash
+# Initial setup (first time only)
+bin/compose setup                         # Installs backend and frontend dependencies
+
+# Starting services
+bin/compose start                         # Start backend and frontend in background
+bin/compose run                           # Start frontend in background, backend in foreground (for debugging with pry)
+
+# Running tests
+bin/compose rspec spec/models/user_spec.rb   # Run specific tests in backend-test container
+
+# Other operations
+bin/compose reset                         # Remove all containers and volumes (requires setup again)
+bin/compose <command>                     # Pass any docker-compose command directly
+```
+
+## Important Notes
+
+- **CRITICAL**: `config/database.yml` must NOT exist when using Docker (rename or delete it)
+- Most developers use a local `docker-compose.override.yml` for custom port mappings and configurations
+- Copy `docker-compose.override.example.yml` to `docker-compose.override.yml` and customize as needed
+- Default ports: Backend at http://localhost:3000 (or 4200 for frontend dev server)
+- Services: `backend`, `frontend`, `worker`, `db`, `db-test`, `backend-test`, `cache`
+- Persisted volumes: `pgdata`, `bundle`, `npm`, `tmp`, `opdata` (data survives container restarts)
+- Docker build context: Uses Dockerfiles in `docker/dev/backend/` and `docker/dev/frontend/`
+
+## Commands Reference
+
+```bash
+# Setup and lifecycle
+bin/compose setup                        # Setup Docker environment (first time)
+bin/compose start                        # Start all services in background
+bin/compose run                          # Start frontend in background, backend in foreground
+bin/compose reset                        # Remove all containers and volumes
+bin/compose stop                         # Stop all services
+bin/compose down                         # Stop and remove containers
+
+# Testing
+bin/compose rspec spec/models/user_spec.rb    # Run specific tests
+bin/compose exec backend bundle exec rspec    # Run tests directly in backend container
+
+# Development
+bin/compose exec backend bundle exec rails console   # Rails console
+bin/compose logs backend                 # View backend logs
+bin/compose logs -f backend              # Follow backend logs
+bin/compose ps                           # List running containers
+
+# Database
+bin/compose exec backend bundle exec rails db:migrate      # Run migrations
+bin/compose exec backend bundle exec rails db:seed         # Seed data
+
+# Direct docker-compose commands
+bin/compose up -d                        # Start services
+bin/compose restart backend              # Restart backend service
+```
diff --git a/docker/dev/CLAUDE.md b/docker/dev/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/frontend/AGENTS.md b/frontend/AGENTS.md
@@ -0,0 +1,46 @@
+# Frontend
+
+## Directory Structure
+
+- `./src/` - Frontend code
+  - `./src/app/` - Legacy Angular modules/components
+  - `./src/stimulus/` - Stimulus controllers
+  - `./src/turbo/` - Turbo integration
+
+## Configuration Files
+
+- `eslint.config.mjs` - JavaScript/TypeScript linting
+- `../package.json` / `./frontend/package.json` - Node.js dependencies
+
+## Version Requirements
+
+- Node: `^22.21.0` (see `package.json` engines)
+
+## Setup
+
+```bash
+npm ci && cd ..   # Install Node packages
+```
+
+## Code Style
+
+### JavaScript/TypeScript
+
+- **New development**: Use Hotwire (Turbo + Stimulus) with server-rendered HTML
+- **Legacy code**: Follow ESLint rules
+- Prefer TypeScript over JavaScript
+- Use [Primer Design System](https://primer.style/product/) via ViewComponent
+
+## Linting
+
+```bash
+# JavaScript/TypeScript
+npx eslint src/ && cd ..
+```
+
+## Testing
+
+```bash
+# Frontend (Jasmine/Karma)
+npm test && cd ..
+```
diff --git a/frontend/CLAUDE.md b/frontend/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/spec/AGENTS.md b/spec/AGENTS.md
@@ -0,0 +1,32 @@
+# Spec
+
+## Directory Structure
+
+- `spec/features/` - System/feature tests (Capybara)
+- `spec/models/` - Model unit tests
+- `spec/requests/` - API/integration tests
+- `spec/services/` - Service tests
+
+## Running Tests
+
+```bash
+# Backend (RSpec) - prefer specific tests over running all
+bundle exec rspec spec/models/user_spec.rb              # Single file
+bundle exec rspec spec/models/user_spec.rb:42           # Single line
+bundle exec rspec spec/features                         # Directory
+RAILS_ENV=test ./bin/rails parallel:spec                # Parallel execution
+```
+
+### Docker
+
+```bash
+bin/compose rspec spec/models/user_spec.rb   # Run specific tests in backend-test container
+bin/compose exec backend bundle exec rspec    # Run tests directly in backend container
+```
+
+## Debugging CI Failures
+
+```bash
+./script/github_pr_errors | xargs bundle exec rspec    # Run failed tests from CI
+./script/bulk_run_rspec spec/path/to/flaky_spec.rb     # Run tests multiple times
+```
diff --git a/spec/CLAUDE.md b/spec/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
