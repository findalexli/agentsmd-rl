#!/usr/bin/env bash
set -euo pipefail

cd /workspace/apps

# Idempotency guard
if grep -qF "**Use Cases**: Webhook handlers delegate to use case classes that contain busine" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "This is a Saleor SMTP Application that handles email notifications for e-commerc" "apps/smtp/AGENTS.md" && grep -qF "apps/smtp/CLAUDE.md" "apps/smtp/CLAUDE.md" && grep -qF "apps/smtp/CLAUDE.md" "apps/smtp/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,124 @@
+# Saleor Apps
+
+## Project Structure
+
+**Monorepo Architecture**: This is a Turborepo-managed monorepo containing Saleor Apps built with Next.js, TypeScript, and modern development tooling.
+
+- `/apps/` - Individual Saleor applications (AvaTax, CMS, Klaviyo, Products Feed, Search, Segment, SMTP, Stripe, NP Atobarai)
+- `/packages/` - Shared libraries and utilities (domain, errors, logger, otel, UI components, etc.)
+- `/templates/` - App templates for new development
+- Uses PNPM workspaces with workspace dependencies via `workspace:*`
+
+**Domain-Driven Design**: Each app follows modular architecture:
+
+- `src/modules/` - Domain-specific business logic modules
+- `src/app/api/` - Next.js App Router API routes (webhooks)
+- `src/pages/` - Legacy Pages Router for some apps
+- Business logic encapsulated in domain entities and use cases
+
+## Essential Commands
+
+**Development**:
+
+- `pnpm dev` - Start all apps in development mode
+- `pnpm --filter <app-name> dev` - Start specific app (e.g., `pnpm --filter saleor-app-avatax dev`)
+- `pnpm dev:debug` - Start with debug logging (app-level)
+
+**Building & Type Checking**:
+
+- `pnpm build` - Build all apps and packages
+- `pnpm check-types` - Type check all projects
+- `tsc --noEmit` - Type check specific app (run in app directory)
+
+**Testing**:
+
+- `pnpm test:ci` - Run unit tests for all projects
+- `vitest --project units` - Run unit tests for specific app
+- `vitest --project e2e` - Run E2E tests for specific app
+- `pnpm e2e` - Run E2E tests (app-level)
+
+**Linting & Formatting**:
+
+- `pnpm lint` - Lint all projects
+- `pnpm lint:fix` - Auto-fix linting issues
+- `pnpm format` - Format all code with Prettier
+- `eslint .` - Lint specific app (run in app directory)
+
+**Code Generation**:
+
+- `pnpm generate` - Generate GraphQL types for all projects
+- `pnpm run generate:app` - Generate app-specific GraphQL types
+- `pnpm run generate:e2e` - Generate E2E test GraphQL types
+
+## Architecture Patterns
+
+**Result-Based Error Handling**: Uses `neverthrow` library extensively. Functions return `Result<T, E>` instead of throwing exceptions:
+
+- Test success: `result._unsafeUnwrap()`
+- Test errors: `result._unsafeUnwrapErr()`
+
+**Branded Types with Zod**: Follow ADR 0002 for type safety on primitives:
+
+```typescript
+const saleorApiUrlSchema = z.string().url().endsWith("/graphql/").brand("SaleorApiUrl");
+export const createSaleorApiUrl = (raw: string) => saleorApiUrlSchema.parse(raw);
+```
+
+**Error Classes**: Use `BaseError.subclass()` pattern from `@saleor/apps-errors`:
+
+```typescript
+static ValidationError = BaseError.subclass("ValidationError", {
+  props: { _brand: "AppChannelConfig.ValidationError" as const },
+});
+```
+
+**Repository Pattern**: Data access through repository interfaces, typically backed by DynamoDB via `@saleor/dynamo-config-repository`.
+
+**Use Cases**: Webhook handlers delegate to use case classes that contain business logic. Use cases extend `BaseUseCase` for shared config loading patterns.
+
+## Key Technologies
+
+**Frontend**: Next.js (App Router + Pages Router), React, TypeScript, Macaw UI, React Hook Form with Zod resolvers
+
+**Backend**: tRPC for type-safe API layer, GraphQL with code generation, Webhook handling
+
+**Database**: DynamoDB for configuration storage, repositories for data access
+
+**Testing**: Vitest with workspace configuration, React Testing Library, PactumJS for E2E tests
+
+**Observability**: OpenTelemetry instrumentation, Sentry error tracking, structured logging with contextual loggers
+
+**Tooling**: Turborepo, PNPM workspaces, ESLint with custom configs, Prettier
+
+## Testing Conventions
+
+**Unit Tests**: Located in `src/**/*.test.ts`, use Vitest with jsdom environment
+**E2E Tests**: Located in `e2e/**/*.spec.ts`, use PactumJS for API testing
+**Setup**: Apps use `src/setup-tests.ts` for unit test setup, `e2e/setup.ts` for E2E setup
+**Mocking**: Mock objects in `src/__tests__/mocks/`, use `vi.spyOn()` for method spying
+
+## Integration Points
+
+**Saleor Integration**: Apps receive webhooks at `/api/webhooks/saleor/`, use webhook definitions in `webhooks.ts` for registration
+
+**External APIs**: Payment providers (Stripe, NP Atobarai), tax services (AvaTax), CMS systems, etc. wrapped in domain-specific client classes
+
+**Configuration**: Apps store configuration in DynamoDB, access via repository pattern with app metadata management
+
+## Development Workflow
+
+1. **Environment Setup**: Each app has `.env.example` - copy to `.env.local` with required values
+2. **Schema Generation**: Run `pnpm generate` after GraphQL schema changes
+3. **Type Safety**: All apps use strict TypeScript - ensure no `any` types
+4. **Testing**: Write unit tests alongside features, E2E tests for critical workflows
+5. **Linting**: Code must pass ESLint rules including custom app-specific rules like `n/no-process-env`
+
+## App-Specific Notes
+
+- **AvaTax**: Tax calculation service with comprehensive E2E testing suite
+- **Stripe**: Payment processing with transaction handling use cases
+- **Search**: Algolia integration with webhook-driven product indexing
+- **SMTP**: Email service with template management
+- **CMS**: Content management system integration with bulk sync capabilities
+
+Run commands from the root directory for global operations, or from individual app directories for app-specific tasks.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,126 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Structure
-
-**Monorepo Architecture**: This is a Turborepo-managed monorepo containing Saleor Apps built with Next.js, TypeScript, and modern development tooling.
-
-- `/apps/` - Individual Saleor applications (AvaTax, CMS, Klaviyo, Products Feed, Search, Segment, SMTP, Stripe, NP Atobarai)
-- `/packages/` - Shared libraries and utilities (domain, errors, logger, otel, UI components, etc.)
-- `/templates/` - App templates for new development
-- Uses PNPM workspaces with workspace dependencies via `workspace:*`
-
-**Domain-Driven Design**: Each app follows modular architecture:
-
-- `src/modules/` - Domain-specific business logic modules
-- `src/app/api/` - Next.js App Router API routes (webhooks)
-- `src/pages/` - Legacy Pages Router for some apps
-- Business logic encapsulated in domain entities and use cases
-
-## Essential Commands
-
-**Development**:
-
-- `pnpm dev` - Start all apps in development mode
-- `pnpm --filter <app-name> dev` - Start specific app (e.g., `pnpm --filter saleor-app-avatax dev`)
-- `pnpm dev:debug` - Start with debug logging (app-level)
-
-**Building & Type Checking**:
-
-- `pnpm build` - Build all apps and packages
-- `pnpm check-types` - Type check all projects
-- `tsc --noEmit` - Type check specific app (run in app directory)
-
-**Testing**:
-
-- `pnpm test:ci` - Run unit tests for all projects
-- `vitest --project units` - Run unit tests for specific app
-- `vitest --project e2e` - Run E2E tests for specific app
-- `pnpm e2e` - Run E2E tests (app-level)
-
-**Linting & Formatting**:
-
-- `pnpm lint` - Lint all projects
-- `pnpm lint:fix` - Auto-fix linting issues
-- `pnpm format` - Format all code with Prettier
-- `eslint .` - Lint specific app (run in app directory)
-
-**Code Generation**:
-
-- `pnpm generate` - Generate GraphQL types for all projects
-- `pnpm run generate:app` - Generate app-specific GraphQL types
-- `pnpm run generate:e2e` - Generate E2E test GraphQL types
-
-## Architecture Patterns
-
-**Result-Based Error Handling**: Uses `neverthrow` library extensively. Functions return `Result<T, E>` instead of throwing exceptions:
-
-- Test success: `result._unsafeUnwrap()`
-- Test errors: `result._unsafeUnwrapErr()`
-
-**Branded Types with Zod**: Follow ADR 0002 for type safety on primitives:
-
-```typescript
-const saleorApiUrlSchema = z.string().url().endsWith("/graphql/").brand("SaleorApiUrl");
-export const createSaleorApiUrl = (raw: string) => saleorApiUrlSchema.parse(raw);
-```
-
-**Error Classes**: Use `BaseError.subclass()` pattern from `@saleor/apps-errors`:
-
-```typescript
-static ValidationError = BaseError.subclass("ValidationError", {
-  props: { _brand: "AppChannelConfig.ValidationError" as const },
-});
-```
-
-**Repository Pattern**: Data access through repository interfaces, typically backed by DynamoDB via `@saleor/dynamo-config-repository`.
-
-**Use Cases**: Webhook handlers delegate to use case classes that contain business logic. Use cases extend `BaseUseCase` for shared config loading patterns.
-
-## Key Technologies
-
-**Frontend**: Next.js (App Router + Pages Router), React, TypeScript, Macaw UI, React Hook Form with Zod resolvers
-
-**Backend**: tRPC for type-safe API layer, GraphQL with code generation, Webhook handling
-
-**Database**: DynamoDB for configuration storage, repositories for data access
-
-**Testing**: Vitest with workspace configuration, React Testing Library, PactumJS for E2E tests
-
-**Observability**: OpenTelemetry instrumentation, Sentry error tracking, structured logging with contextual loggers
-
-**Tooling**: Turborepo, PNPM workspaces, ESLint with custom configs, Prettier
-
-## Testing Conventions
-
-**Unit Tests**: Located in `src/**/*.test.ts`, use Vitest with jsdom environment
-**E2E Tests**: Located in `e2e/**/*.spec.ts`, use PactumJS for API testing
-**Setup**: Apps use `src/setup-tests.ts` for unit test setup, `e2e/setup.ts` for E2E setup
-**Mocking**: Mock objects in `src/__tests__/mocks/`, use `vi.spyOn()` for method spying
-
-## Integration Points
-
-**Saleor Integration**: Apps receive webhooks at `/api/webhooks/saleor/`, use webhook definitions in `webhooks.ts` for registration
-
-**External APIs**: Payment providers (Stripe, NP Atobarai), tax services (AvaTax), CMS systems, etc. wrapped in domain-specific client classes
-
-**Configuration**: Apps store configuration in DynamoDB, access via repository pattern with app metadata management
-
-## Development Workflow
-
-1. **Environment Setup**: Each app has `.env.example` - copy to `.env.local` with required values
-2. **Schema Generation**: Run `pnpm generate` after GraphQL schema changes
-3. **Type Safety**: All apps use strict TypeScript - ensure no `any` types
-4. **Testing**: Write unit tests alongside features, E2E tests for critical workflows
-5. **Linting**: Code must pass ESLint rules including custom app-specific rules like `n/no-process-env`
-
-## App-Specific Notes
-
-- **AvaTax**: Tax calculation service with comprehensive E2E testing suite
-- **Stripe**: Payment processing with transaction handling use cases
-- **Search**: Algolia integration with webhook-driven product indexing
-- **SMTP**: Email service with template management
-- **CMS**: Content management system integration with bulk sync capabilities
-
-Run commands from the root directory for global operations, or from individual app directories for app-specific tasks.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
diff --git a/apps/smtp/AGENTS.md b/apps/smtp/AGENTS.md
@@ -0,0 +1,109 @@
+# Saleor App SMTP
+
+## Project Overview
+
+This is a Saleor SMTP Application that handles email notifications for e-commerce events. It integrates with Saleor API via webhooks and sends transactional emails using SMTP configuration.
+
+## Key Commands
+
+### Development
+
+- `pnpm install` - Install dependencies
+- `pnpm dev` - Start development server (available at http://localhost:3000)
+- `pnpm build` - Build the application
+- `pnpm start` - Start production server
+
+### Code Quality
+
+- `pnpm lint` - Run ESLint
+- `pnpm lint:fix` - Auto-fix linting issues
+- `pnpm check-types` - Type checking with TypeScript
+
+### Testing
+
+- `pnpm test` - Run tests with Vitest in watch mode
+- `pnpm test:ci` - Run tests once with coverage
+- To run a single test file: `pnpm test <filename>`
+
+### GraphQL
+
+- `pnpm fetch-schema` - Update GraphQL schema from Saleor
+- `pnpm generate` - Generate TypeScript for GraphQL, after changing queries, mutations, schema
+
+## Architecture
+
+### Tech Stack
+
+- **Framework**: Next.js with TypeScript
+- **API Layer**: tRPC for type-safe APIs
+- **GraphQL**: URQL client with code generation
+- **Database**: DynamoDB (with support for multiple APL storages - used when installing app)
+- **Email Processing**: MJML for responsive email templates, Handlebars and `handlebars-helpers` for templating
+- **Testing**: Vitest with React Testing Library
+- **Monitoring**: Sentry and OpenTelemetry
+
+### Directory Structure
+
+- `/src/pages` - Next.js pages and API routes
+- `/src/modules` - Feature modules with business logic
+  - `smtp/` - Email configuration and sending logic
+  - `trpc/` - tRPC setup and procedures
+  - `webhook-management/` - Webhook handling
+  - `dynamodb/` - Database client
+  - `event-handlers/` - Event processing logic
+- `/src/lib` - Shared utilities and helpers
+- `/graphql` - GraphQL schema and operations
+- `/generated` - Auto-generated GraphQL types
+
+### Key Architectural Patterns
+
+#### tRPC Router Pattern
+
+All API endpoints use tRPC routers defined in `*.router.ts` files. Protected procedures require authentication via `protectedClientProcedure` (valid Saleor token).
+
+#### Event-Driven Architecture
+
+The app responds to Saleor events through webhooks:
+
+- Order events (created, confirmed, cancelled, fulfilled, etc.)
+- Invoice events
+- Gift card events
+  Each event type has its own handler in `/src/pages/api/webhooks/`
+
+#### SMTP Configuration Service
+
+Located in `/src/modules/smtp/configuration/`, manages email templates and SMTP settings per event type. Configurations are stored in DynamoDB/APL.
+
+#### Email Compilation Pipeline
+
+1. HandlebarsTemplateCompiler - Process Handlebars variables
+2. MjmlCompiler - Convert MJML to HTML
+3. HtmlToTextCompiler - Generate text version
+4. SmtpEmailSender - Send via Nodemailer
+
+### Environment Configuration
+
+The app supports multiple APL (Auth Persistence Layer) options:
+
+- `file` - Local development (default)
+- `upstash` - Production with Redis
+- `dynamodb` - AWS DynamoDB
+- `saleor-cloud` - Saleor Cloud APL
+
+Set via `APL` environment variable in `.env` file.
+
+### Testing Approach
+
+- Unit tests use Vitest with mocked dependencies
+- Tests are colocated with source files (`.test.ts`)
+- Use `describe`, `it`, `expect` from Vitest
+- Mock external services and APIs
+- Tests run with shuffled order to prevent side effects
+
+### Important Notes
+
+- Always commit the `/generated` folder after GraphQL changes
+- The app requires Saleor version >=3.11.7 <4
+- Use ngrok for local webhook testing
+- MJML templates support Handlebars variables for dynamic content
+- All webhook handlers are in `/src/pages/api/webhooks/`
diff --git a/apps/smtp/CLAUDE.md b/apps/smtp/CLAUDE.md
@@ -1,96 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-This is a Saleor SMTP Application that handles email notifications for e-commerce events. It integrates with Saleor API via webhooks and sends transactional emails using SMTP configuration.
-
-## Key Commands
-
-### Development
-- `pnpm install` - Install dependencies
-- `pnpm dev` - Start development server (available at http://localhost:3000)
-- `pnpm build` - Build the application
-- `pnpm start` - Start production server
-
-### Code Quality
-- `pnpm lint` - Run ESLint
-- `pnpm lint:fix` - Auto-fix linting issues
-- `pnpm check-types` - Type checking with TypeScript
-
-### Testing
-- `pnpm test` - Run tests with Vitest in watch mode
-- `pnpm test:ci` - Run tests once with coverage
-- To run a single test file: `pnpm test <filename>`
-
-### GraphQL
-- `pnpm fetch-schema` - Update GraphQL schema from Saleor
-- `pnpm generate` - Generate TypeScript for GraphQL, after changing queries, mutations, schema
-
-## Architecture
-
-### Tech Stack
-- **Framework**: Next.js with TypeScript
-- **API Layer**: tRPC for type-safe APIs
-- **GraphQL**: URQL client with code generation
-- **Database**: DynamoDB (with support for multiple APL storages - used when installing app)
-- **Email Processing**: MJML for responsive email templates, Handlebars and `handlebars-helpers` for templating
-- **Testing**: Vitest with React Testing Library
-- **Monitoring**: Sentry and OpenTelemetry
-
-### Directory Structure
-- `/src/pages` - Next.js pages and API routes
-- `/src/modules` - Feature modules with business logic
-  - `smtp/` - Email configuration and sending logic
-  - `trpc/` - tRPC setup and procedures
-  - `webhook-management/` - Webhook handling
-  - `dynamodb/` - Database client
-  - `event-handlers/` - Event processing logic
-- `/src/lib` - Shared utilities and helpers
-- `/graphql` - GraphQL schema and operations
-- `/generated` - Auto-generated GraphQL types
-
-### Key Architectural Patterns
-
-#### tRPC Router Pattern
-All API endpoints use tRPC routers defined in `*.router.ts` files. Protected procedures require authentication via `protectedClientProcedure` (valid Saleor token).
-
-#### Event-Driven Architecture
-The app responds to Saleor events through webhooks:
-- Order events (created, confirmed, cancelled, fulfilled, etc.)
-- Invoice events
-- Gift card events
-Each event type has its own handler in `/src/pages/api/webhooks/`
-
-#### SMTP Configuration Service
-Located in `/src/modules/smtp/configuration/`, manages email templates and SMTP settings per event type. Configurations are stored in DynamoDB/APL.
-
-#### Email Compilation Pipeline
-1. HandlebarsTemplateCompiler - Process Handlebars variables
-2. MjmlCompiler - Convert MJML to HTML
-3. HtmlToTextCompiler - Generate text version
-4. SmtpEmailSender - Send via Nodemailer
-
-### Environment Configuration
-
-The app supports multiple APL (Auth Persistence Layer) options:
-- `file` - Local development (default)
-- `upstash` - Production with Redis
-- `dynamodb` - AWS DynamoDB
-- `saleor-cloud` - Saleor Cloud APL
-
-Set via `APL` environment variable in `.env` file.
-
-### Testing Approach
-- Unit tests use Vitest with mocked dependencies
-- Tests are colocated with source files (`.test.ts`)
-- Use `describe`, `it`, `expect` from Vitest
-- Mock external services and APIs
-- Tests run with shuffled order to prevent side effects
-
-### Important Notes
-- Always commit the `/generated` folder after GraphQL changes
-- The app requires Saleor version >=3.11.7 <4
-- Use ngrok for local webhook testing
-- MJML templates support Handlebars variables for dynamic content
-- All webhook handlers are in `/src/pages/api/webhooks/`
diff --git a/apps/smtp/CLAUDE.md b/apps/smtp/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
