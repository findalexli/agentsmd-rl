#!/usr/bin/env bash
set -euo pipefail

cd /workspace/packmind

# Idempotency guard
if grep -qF "The following commands apply for both NX apps and packages (use `./node_modules/" "AGENTS.md" && grep -qF "The following commands apply for both NX apps and packages (use `./node_modules/" "CLAUDE.md" && grep -qF "- Build an application: `./node_modules/.bin/nx build <app-name>`" "apps/AGENTS.md" && grep -qF "- Build an application: `./node_modules/.bin/nx build <app-name>`" "apps/CLAUDE.md" && grep -qF "- Type check: `./node_modules/.bin/nx typecheck api`" "apps/api/AGENTS.md" && grep -qF "- Type check: `./node_modules/.bin/nx typecheck api`" "apps/api/CLAUDE.md" && grep -qF "- Build: `./node_modules/.bin/nx build packmind-cli`" "apps/cli/AGENTS.md" && grep -qF "- Build: `./node_modules/.bin/nx build packmind-cli`" "apps/cli/CLAUDE.md" && grep -qF "- Type check: `./node_modules/.bin/nx typecheck frontend`" "apps/frontend/AGENTS.md" && grep -qF "- Type check: `./node_modules/.bin/nx typecheck frontend`" "apps/frontend/CLAUDE.md" && grep -qF "- Type check: `./node_modules/.bin/nx typecheck mcp-server`" "apps/mcp-server/AGENTS.md" && grep -qF "- Type check: `./node_modules/.bin/nx typecheck mcp-server`" "apps/mcp-server/CLAUDE.md" && grep -qF "- Build a package: `./node_modules/.bin/nx build <package-name>`" "packages/AGENTS.md" && grep -qF "- Build a package: `./node_modules/.bin/nx build <package-name>`" "packages/CLAUDE.md" && grep -qF "- Build: `./node_modules/.bin/nx build ui`" "packages/ui/AGENTS.md" && grep -qF "- Build: `./node_modules/.bin/nx build ui`" "packages/ui/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -9,7 +9,7 @@ This is an Nx monorepo containing applications and reusable packages.
 - **Database**: PostgreSQL with TypeORM for entity persistence
 - **Cache**: Redis for caching
 - **Background Jobs**: BullMQ for job queue management
-- **Testing**: Jest with @swc/jest as test runner. Tests are run with `nx run <project-name>` as detailed below.
+- **Testing**: Jest with @swc/jest as test runner. Tests are run with `./node_modules/.bin/nx run <project-name>` as detailed below.
 
 ## Directory Structure
 
@@ -27,20 +27,18 @@ docker compose up
 
 This starts the entire development environment.
 Docker Compose automatically provisions PostgreSQL and Redis - no manual setup required.
-Don't use `nx serve` commands for local development, let user starts the stack with `docker compose up`
-
 ## Working with Nx
 
-The following commands apply for both NX apps and packages (use `nx show projects` to list actual apps and packages.)
-- Test a project: `nx test <project-name>`
-- Lint a project: `nx lint <project-name>`
-- Build a project: `nx build <project-name>`
+The following commands apply for both NX apps and packages (use `./node_modules/.bin/nx show projects` to list actual apps and packages.)
+- Test a project: `./node_modules/.bin/nx test <project-name>`
+- Lint a project: `./node_modules/.bin/nx lint <project-name>`
+- Build a project: `./node_modules/.bin/nx build <project-name>`
 - Test affected projects: `npm run test:staged`
 - Lint affected projects: `npm run lint:staged`
 
 ## Code Quality
 
-- **Linting**: `nx lint <project-name>` runs ESLint, using the config file `eslint.config.mjs`.
+- **Linting**: `./node_modules/.bin/nx lint <project-name>` runs ESLint, using the config file `eslint.config.mjs`.
 - **Formatting**: Prettier is used for code formatting. You don't have to run it, it's set as a pre-commit hook.
 
 ## Commands
@@ -69,7 +67,7 @@ Public end-user documentation is maintained in the `apps/doc/` folder (Mintlify-
 
 - For any task you perform, you MUST split it into multiple into sub-tasks which have a logical increment (eg: new endpoint, new component, new use case etc). When a task is done, run all the validation steps (lint, test, packmind etc) and ask me for validation of the work you did.
 - Each sub task MUST have its own commit.
-- Use the `nx lint` and `nx test` commands on the apps and packages you've edited
+- Use the `./node_modules/.bin/nx lint` and `./node_modules/.bin/nx test` commands on the apps and packages you've edited
 
 <!-- start: Packmind standards -->
 # Packmind Standards
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -9,7 +9,7 @@ This is an Nx monorepo containing applications and reusable packages.
 - **Database**: PostgreSQL with TypeORM for entity persistence
 - **Cache**: Redis for caching
 - **Background Jobs**: BullMQ for job queue management
-- **Testing**: Jest with @swc/jest as test runner. Tip: use `nx show projects` to list actual apps and packages.
+- **Testing**: Jest with @swc/jest as test runner. Tip: use `./node_modules/.bin/nx show projects` to list actual apps and packages.
 
 ## Directory Structure
 
@@ -21,19 +21,18 @@ This is an Nx monorepo containing applications and reusable packages.
 
 Local development uses Docker Compose to run all services (API, frontend, database, Redis, mcp-Server, Postgresq).
 This starts the entire development environmentDocker Compose automatically provisions PostgreSQL and Redis - no manual setup required.
-Do not use nx serve commands for regular local development. Use docker compose up to start the full development environment. Only use `nx serve <app>` for isolated testing of a single application.
 ## Working with Nx
 
-The following commands apply for both NX apps and packages (use `nx show projects` to list actual apps and packages.)
-- Test a project: `nx test <project-name>`
-- Lint a project: `nx lint <project-name>`
-- Build a project: `nx build <project-name>`
+The following commands apply for both NX apps and packages (use `./node_modules/.bin/nx show projects` to list actual apps and packages.)
+- Test a project: `./node_modules/.bin/nx test <project-name>`
+- Lint a project: `./node_modules/.bin/nx lint <project-name>`
+- Build a project: `./node_modules/.bin/nx build <project-name>`
 - Test affected projects: `npm run test:staged`
 - Lint affected projects: `npm run lint:staged`
 
 ## Code Quality
 
-- **Linting**: `nx lint <project-name>` runs ESLint, using the config file `eslint.config.mjs`.
+- **Linting**: `./node_modules/.bin/nx lint <project-name>` runs ESLint, using the config file `eslint.config.mjs`.
 - **Formatting**: Prettier is used for code formatting. You don't have to run it, it's set as a pre-commit hook.
 
 ## Commands
@@ -63,5 +62,5 @@ Public end-user documentation is maintained in the `apps/doc/` folder (Mintlify-
 
 - For any task you perform, you MUST split it into multiple into sub-tasks which have a logical increment (eg: new endpoint, new component, new use case etc). When a task is done, run all the validation steps (lint, test, packmind etc) and ask me for validation of the work you did.
 - Each sub task MUST have its own commit.
-- Use the `nx lint` and `nx test` commands on the apps and packages you've edited
+- Use the `./node_modules/.bin/nx lint` and `./node_modules/.bin/nx test` commands on the apps and packages you've edited
 
diff --git a/apps/AGENTS.md b/apps/AGENTS.md
@@ -23,9 +23,8 @@ This directory contains all deployable applications in the Packmind monorepo.
 
 ### Common Nx Commands
 
-- Build an application: `nx build <app-name>`
-- Test an application: `nx test <app-name>`
-- Lint an application: `nx lint <app-name>`
-- Serve/dev an application: `nx serve <app-name>` or `nx dev <app-name>`
+- Build an application: `./node_modules/.bin/nx build <app-name>`
+- Test an application: `./node_modules/.bin/nx test <app-name>`
+- Lint an application: `./node_modules/.bin/nx lint <app-name>`
 
 **Available applications**: `api`, `mcp-server`, `frontend`, `cli`, `e2e-tests`, `doc`
diff --git a/apps/CLAUDE.md b/apps/CLAUDE.md
@@ -23,9 +23,8 @@ This directory contains all deployable applications in the Packmind monorepo.
 
 ### Common Nx Commands
 
-- Build an application: `nx build <app-name>`
-- Test an application: `nx test <app-name>`
-- Lint an application: `nx lint <app-name>`
-- Serve/dev an application: `nx serve <app-name>` or `nx dev <app-name>`
+- Build an application: `./node_modules/.bin/nx build <app-name>`
+- Test an application: `./node_modules/.bin/nx test <app-name>`
+- Lint an application: `./node_modules/.bin/nx lint <app-name>`
 
 **Available applications**: `api`, `mcp-server`, `frontend`, `cli`, `e2e-tests`, `doc`
diff --git a/apps/api/AGENTS.md b/apps/api/AGENTS.md
@@ -23,12 +23,10 @@ Main backend API for Packmind, built with NestJS and hexagonal architecture.
 
 ## Main Commands
 
-- Build: `nx build api`
-- Test: `nx test api`
-- Serve (development): `nx serve api` *(for isolated testing only; use `docker compose up` for regular local development)*
-- Start (production): `nx start api`
-- Type check: `nx typecheck api`
-- Lint: `nx lint api`
+- Build: `./node_modules/.bin/nx build api`
+- Test: `./node_modules/.bin/nx test api`
+- Type check: `./node_modules/.bin/nx typecheck api`
+- Lint: `./node_modules/.bin/nx lint api`
 
 ## Configuration
 
diff --git a/apps/api/CLAUDE.md b/apps/api/CLAUDE.md
@@ -23,12 +23,10 @@ Main backend API for Packmind, built with NestJS and hexagonal architecture.
 
 ## Main Commands
 
-- Build: `nx build api`
-- Test: `nx test api`
-- Serve (development): `nx serve api` *(for isolated testing only; use `docker compose up` for regular local development)*
-- Start (production): `nx start api`
-- Type check: `nx typecheck api`
-- Lint: `nx lint api`
+- Build: `./node_modules/.bin/nx build api`
+- Test: `./node_modules/.bin/nx test api`
+- Type check: `./node_modules/.bin/nx typecheck api`
+- Lint: `./node_modules/.bin/nx lint api`
 
 ## Configuration
 
diff --git a/apps/cli/AGENTS.md b/apps/cli/AGENTS.md
@@ -25,11 +25,11 @@ Command-line interface for Packmind, built with cmd-ts and tree-sitter parsers.
 
 ## Main Commands
 
-- Build: `nx build packmind-cli`
-- Test: `nx test packmind-cli`
+- Build: `./node_modules/.bin/nx build packmind-cli`
+- Test: `./node_modules/.bin/nx test packmind-cli`
 - Build npm executable (current platform): `npm run packmind-cli:build`
 - Build portable bun executables: `bun run apps/cli/bun-build.ts --target=all`
-- Lint: `nx lint packmind-cli`
+- Lint: `./node_modules/.bin/nx lint packmind-cli`
 
 <!-- start: Packmind standards -->
 # Packmind Standards
diff --git a/apps/cli/CLAUDE.md b/apps/cli/CLAUDE.md
@@ -25,8 +25,8 @@ Command-line interface for Packmind, built with cmd-ts and tree-sitter parsers.
 
 ## Main Commands
 
-- Build: `nx build packmind-cli`
-- Test: `nx test packmind-cli`
+- Build: `./node_modules/.bin/nx build packmind-cli`
+- Test: `./node_modules/.bin/nx test packmind-cli`
 - Build npm executable (current platform): `npm run packmind-cli:build`
 - Build portable bun executables: `bun run apps/cli/bun-build.ts --target=all`
-- Lint: `nx lint packmind-cli`
+- Lint: `./node_modules/.bin/nx lint packmind-cli`
diff --git a/apps/frontend/AGENTS.md b/apps/frontend/AGENTS.md
@@ -23,11 +23,10 @@ React Router v7 single-page application for Packmind, built with Chakra UI and T
 
 ## Main Commands
 
-- Build: `nx build frontend`
-- Test: `nx test frontend`
-- Dev server: `nx dev frontend` *(for isolated testing only; use `docker compose up` for regular local development)*
-- Type check: `nx typecheck frontend`
-- Lint: `nx lint frontend`
+- Build: `./node_modules/.bin/nx build frontend`
+- Test: `./node_modules/.bin/nx test frontend`
+- Type check: `./node_modules/.bin/nx typecheck frontend`
+- Lint: `./node_modules/.bin/nx lint frontend`
 
 ## Configuration
 
diff --git a/apps/frontend/CLAUDE.md b/apps/frontend/CLAUDE.md
@@ -23,11 +23,10 @@ React Router v7 single-page application for Packmind, built with Chakra UI and T
 
 ## Main Commands
 
-- Build: `nx build frontend`
-- Test: `nx test frontend`
-- Dev server: `nx dev frontend` *(for isolated testing only; use `docker compose up` for regular local development)*
-- Type check: `nx typecheck frontend`
-- Lint: `nx lint frontend`
+- Build: `./node_modules/.bin/nx build frontend`
+- Test: `./node_modules/.bin/nx test frontend`
+- Type check: `./node_modules/.bin/nx typecheck frontend`
+- Lint: `./node_modules/.bin/nx lint frontend`
 
 ## Configuration
 
diff --git a/apps/mcp-server/AGENTS.md b/apps/mcp-server/AGENTS.md
@@ -29,11 +29,10 @@ Model Context Protocol server exposing Packmind capabilities to AI coding agents
 
 ## Main Commands
 
-- Build: `nx build mcp-server`
-- Test: `nx test mcp-server`
-- Serve (development): `nx serve mcp-server` *(for isolated testing only; use `docker compose up` for regular local development)*
-- Type check: `nx typecheck mcp-server`
-- Lint: `nx lint mcp-server`
+- Build: `./node_modules/.bin/nx build mcp-server`
+- Test: `./node_modules/.bin/nx test mcp-server`
+- Type check: `./node_modules/.bin/nx typecheck mcp-server`
+- Lint: `./node_modules/.bin/nx lint mcp-server`
 
 ## Configuration
 
diff --git a/apps/mcp-server/CLAUDE.md b/apps/mcp-server/CLAUDE.md
@@ -29,11 +29,10 @@ Model Context Protocol server exposing Packmind capabilities to AI coding agents
 
 ## Main Commands
 
-- Build: `nx build mcp-server`
-- Test: `nx test mcp-server`
-- Serve (development): `nx serve mcp-server` *(for isolated testing only; use `docker compose up` for regular local development)*
-- Type check: `nx typecheck mcp-server`
-- Lint: `nx lint mcp-server`
+- Build: `./node_modules/.bin/nx build mcp-server`
+- Test: `./node_modules/.bin/nx test mcp-server`
+- Type check: `./node_modules/.bin/nx typecheck mcp-server`
+- Lint: `./node_modules/.bin/nx lint mcp-server`
 
 ## Configuration
 
diff --git a/packages/AGENTS.md b/packages/AGENTS.md
@@ -46,9 +46,9 @@ This directory contains reusable domain and infrastructure packages shared acros
 
 ### Common Nx Commands
 
-- Build a package: `nx build <package-name>`
-- Test a package: `nx test <package-name>`
-- Lint a package: `nx lint <package-name>`
+- Build a package: `./node_modules/.bin/nx build <package-name>`
+- Test a package: `./node_modules/.bin/nx test <package-name>`
+- Lint a package: `./node_modules/.bin/nx lint <package-name>`
 
 **Example packages**: `types`, `logger`, `accounts`, `standards`, `ui`, `node-utils`, `test-utils`
 
diff --git a/packages/CLAUDE.md b/packages/CLAUDE.md
@@ -46,8 +46,8 @@ This directory contains reusable domain and infrastructure packages shared acros
 
 ### Common Nx Commands
 
-- Build a package: `nx build <package-name>`
-- Test a package: `nx test <package-name>`
-- Lint a package: `nx lint <package-name>`
+- Build a package: `./node_modules/.bin/nx build <package-name>`
+- Test a package: `./node_modules/.bin/nx test <package-name>`
+- Lint a package: `./node_modules/.bin/nx lint <package-name>`
 
 **Example packages**: `types`, `logger`, `accounts`, `standards`, `ui`, `node-utils`, `test-utils`
\ No newline at end of file
diff --git a/packages/ui/AGENTS.md b/packages/ui/AGENTS.md
@@ -10,9 +10,9 @@ Reusable UI components built on Chakra UI v3, providing PM-prefixed components f
 
 ## Commands
 
-- Build: `nx build ui`
-- Test: `nx test ui`
-- Lint: `nx lint ui`
+- Build: `./node_modules/.bin/nx build ui`
+- Test: `./node_modules/.bin/nx test ui`
+- Lint: `./node_modules/.bin/nx lint ui`
 
 <!-- start: Packmind standards -->
 # Packmind Standards
diff --git a/packages/ui/CLAUDE.md b/packages/ui/CLAUDE.md
@@ -10,6 +10,6 @@ Reusable UI components built on Chakra UI v3, providing PM-prefixed components f
 
 ## Commands
 
-- Build: `nx build ui`
-- Test: `nx test ui`
-- Lint: `nx lint ui`
+- Build: `./node_modules/.bin/nx build ui`
+- Test: `./node_modules/.bin/nx test ui`
+- Lint: `./node_modules/.bin/nx lint ui`
PATCH

echo "Gold patch applied."
