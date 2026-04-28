#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ask-bonk

# Idempotency guard
if grep -qF "**`/webhooks` - GitHub Actions Mode**: Webhook events trigger GitHub Actions wor" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,32 +2,6 @@
 
 GitHub code review bot built on Cloudflare Workers + Hono + TypeScript. Use `bun` exclusively.
 
-## Architecture
-
-**Cloudflare Workers** application running on the edge (not Node.js). Key constraints:
-
-- No filesystem access (env vars via `process.env` with nodejs_compat)
-- Use Workers-compatible APIs (Fetch, Web Crypto, etc.)
-- Durable Objects for stateful coordination
-
-### Operation Modes
-
-**`/webhooks` - GitHub Actions Mode**: Webhook events trigger GitHub Actions workflows. OpenCode runs _inside the workflow_, not in Bonk's infrastructure. The `RepoAgent` Durable Object tracks workflow run status and posts failure comments.
-
-**`/ask` - Direct Sandbox Mode**: Runs OpenCode directly in Cloudflare Sandbox for programmatic API access. Requires bearer auth (`ASK_SECRET`). Returns SSE stream.
-
-### Key Files
-
-- `src/index.ts` - Hono app entry, webhook handling, request routing
-- `src/github.ts` - GitHub API (Octokit with retry/throttling plugins, GraphQL for context)
-- `src/sandbox.ts` - Cloudflare Sandbox + OpenCode SDK integration
-- `src/workflow.ts` - GitHub Actions workflow mode (creates workflow PRs, tracks runs)
-- `src/agent.ts` - RepoAgent Durable Object for tracking workflow runs
-- `src/events.ts` - Webhook event parsing and response formatting
-- `src/types.ts` - Type definitions (Env, request/response types, GitHub types)
-- `src/oidc.ts` - OIDC token validation and exchange for GitHub Actions
-- `src/log.ts` - Structured logging utility (JSON output, context propagation)
-
 ## Commands
 
 ```bash
@@ -42,62 +16,101 @@ bun run lint             # Lint with oxlint
 bun run format           # Format with oxfmt
 ```
 
-### Test Notes
+When modifying `package.json`, always run `bun install` and commit both `package.json` and `bun.lock` together. CI uses `bun install --frozen-lockfile`.
 
-- Main tests run in `@cloudflare/vitest-pool-workers` (Workers environment)
-- Config: `vitest.config.mts` (main), `test/tsconfig.json` (test-specific)
+## Rules
 
-## Dependency Management
+### Always
 
-**CRITICAL**: When modifying `package.json`, you MUST also update `bun.lock`:
+- Run `bun run tsc --noEmit` and `bun run test` before considering work complete.
+- Use structured logging via `src/log.ts`. Never use raw `console.log/info/error`.
+- Use `Result` types from `better-result` for error handling at API boundaries. Use `TaggedError` subclasses from `src/errors.ts` for domain errors.
+- Use `errorWithException()` for error logging -- it sanitizes secrets automatically.
+- Use `type` imports for type-only imports: `import type { Env } from './types'`.
+- Group imports: external packages first, then local modules.
 
-1. Run `bun install` after modifying `package.json`
-2. Commit both `package.json` AND `bun.lock` together
+### Never
 
-CI uses `bun install --frozen-lockfile` which fails if lockfile doesn't match.
+- Never log tokens, API keys, or credentials. Git error messages may contain URL tokens -- always use `errorWithException()`.
+- Never add new dependencies without justification. This is a small, focused project.
+- Never use Node.js-specific APIs that are unavailable in Cloudflare Workers (no `fs`, no `path`, no `child_process`).
+- Never write tests that mock everything -- tests must exercise real code paths. See [Testing](#testing).
+- Never use raw `console.log/info/error` -- use the structured logger.
 
-## Code Style
+## Architecture
 
-### Formatting (enforced by .editorconfig + oxfmt)
+**Cloudflare Workers** application (not Node.js). Key constraints:
 
-- **Indentation**: 2 spaces
-- **Line endings**: LF
-- **Quotes**: Double quotes
-- **Semicolons**: Required
-- **Final newline**: Required
+- No filesystem access (env vars via `process.env` with `nodejs_compat`)
+- Use Workers-compatible APIs (Fetch, Web Crypto, etc.)
+- Durable Objects for stateful coordination
 
-### Imports
+### Operation Modes
 
-- Group by: external packages first, then local modules
-- Use `type` imports for types only: `import type { Env } from './types'`
+**`/webhooks` - GitHub Actions Mode**: Webhook events trigger GitHub Actions workflows via the composite action in `github/`. OpenCode runs inside the workflow, not in Bonk's infrastructure. The `RepoAgent` Durable Object tracks run status and posts failure comments.
 
-### Types
+**`/ask` - Direct Sandbox Mode**: Runs OpenCode directly in Cloudflare Sandbox for programmatic API access. Requires bearer auth (`ASK_SECRET`). Returns SSE stream.
 
-- Strict mode enabled (`tsconfig.json`)
-- Define shared types in `src/types.ts`
-- Use explicit return types for exported functions
-- Target: ES2024, module resolution: Bundler
+### Project Structure
 
-### Naming
+```
+src/                     # Cloudflare Workers application
+  index.ts               # Hono app entry, all route definitions, webhook handling
+  github.ts              # GitHub API (Octokit with retry/throttling, GraphQL for context)
+  sandbox.ts             # Cloudflare Sandbox + OpenCode SDK integration
+  agent.ts               # RepoAgent Durable Object (workflow run tracking, failure comments)
+  events.ts              # Webhook event parsing and response formatting
+  oidc.ts                # OIDC token validation and GitHub token exchange
+  workflow.ts            # GitHub Actions workflow file management (creates PRs)
+  images.ts              # Image/file extraction from GitHub comment markdown
+  metrics.ts             # Cloudflare Analytics Engine metrics + stats queries
+  errors.ts              # Domain error types (TaggedError subclasses)
+  constants.ts           # Shared configuration constants (retry, polling, limits)
+  types.ts               # All shared type definitions (Env, request/response, GitHub types)
+  log.ts                 # Structured JSON logging (context propagation, secret sanitization)
+  hbs.d.ts               # TypeScript declarations for build-time constants + asset imports
+
+github/                  # GitHub Actions composite action
+  action.yml             # Action definition (mention check, orchestration, opencode run, finalize)
+  script/orchestrate.ts  # Pre-flight: permissions, setup, version, prompt building, OIDC exchange
+  script/finalize.ts     # Post-run: report status back to API (always runs)
+  script/context.ts      # Context helpers for action scripts (env parsing, fork detection)
+  script/http.ts         # HTTP utilities (fetchWithTimeout, fetchWithRetry)
+  fork_guidance.md       # Template for fork PR comment-only mode instructions
+
+cli/                     # Interactive CLI tool (bun run cli)
+  index.ts               # Install + workflow commands using @clack/prompts
+  github.ts              # GitHub API helpers using gh CLI
+  templates/             # Handlebars workflow templates (bonk, scheduled, triage, review, custom)
+
+test/                    # Tests (vitest in @cloudflare/vitest-pool-workers)
+  index.spec.ts          # All tests (event parsing, prompt extraction, OIDC, logging)
+  fixtures/              # Realistic webhook payload fixtures
+
+ae_queries/              # SQL queries for /stats Analytics Engine endpoints
+```
 
-- `camelCase` for functions/variables
-- `PascalCase` for types/classes/interfaces
-- `snake_case` for log event names and log field names
-- Prefix interfaces with descriptive nouns (e.g., `EventContext`, `TrackWorkflowRequest`)
+## Error Handling
 
-### Code Organization
+Use `Result` types from `better-result` instead of thrown exceptions at API boundaries:
 
-- Keep related code together; avoid splitting across too many files
-- Don't over-abstract until there are 2+ clear reuse cases
-- External API functions stay in their respective files (`github.ts`, `sandbox.ts`, `oidc.ts`)
-- Comments explain "why", not "what"; skip for short (<10 line) functions
-- Prioritize comments for I/O boundaries, external system orchestration, and stateful code
+```typescript
+import { Result, Ok, Err } from "better-result";
+import { ValidationError, GitHubAPIError } from "./errors";
 
-## Logging
+function doThing(): Result<Data, ValidationError | GitHubAPIError> {
+  if (!valid) return Err(new ValidationError("bad input"));
+  return Ok(data);
+}
+```
 
-Use structured JSON logging via `src/log.ts`. **Do NOT use raw `console.log/info/error`**.
+All domain errors are `TaggedError` subclasses defined in `src/errors.ts`: `OIDCValidationError`, `AuthorizationError`, `InstallationNotFoundError`, `ValidationError`, `NotFoundError`, `GitHubAPIError`, `SandboxError`. Use `.is()` for pattern matching.
+
+For request handlers, return JSON errors with appropriate HTTP status codes (`{ error: string }`).
+
+## Logging
 
-### Usage
+Use structured JSON logging via `src/log.ts`.
 
 ```typescript
 import { createLogger, log } from "./log";
@@ -109,97 +122,90 @@ requestLog.info("webhook_completed", { event_type: "issue_comment", duration_ms:
 // Child loggers inherit context
 const sessionLog = requestLog.child({ session_id: "abc123" });
 
-// Error logging with exception details
+// Error logging -- sanitizes secrets automatically
 requestLog.errorWithException("operation_failed", error, { additional: "context" });
-
-// Default logger for cases without request context
-log.error("startup_failed", { reason: "missing config" });
 ```
 
-### Event Naming
+- **Event names**: `snake_case`, past tense for completed actions. Prefix with domain when helpful: `sandbox_clone_failed`, `github_rate_limited`.
+- **Required context**: `request_id` (ULID), `owner`, `repo`. Include `issue_number`, `run_id`, `actor`, `duration_ms` when relevant.
+
+## Code Style
 
-- Use `snake_case`: `webhook_received`, `run_tracking_started`, `sandbox_clone_failed`
-- Use past tense for completed actions: `track_completed`, `installation_deleted`
-- Prefix with domain when helpful: `sandbox_prompt_failed`, `github_rate_limited`
+### Formatting (enforced by .editorconfig + oxfmt)
 
-### Required Context Fields
+- 2 spaces, LF line endings, double quotes, semicolons required, final newline required.
 
-- `request_id` - ULID generated at request entry point for correlation
-- `owner`, `repo` - Always include when available
-- `issue_number`, `run_id`, `actor` - Include when relevant
-- `duration_ms` - Include in completion/error logs (wide event pattern)
+### Naming
+
+- `camelCase` for functions/variables
+- `PascalCase` for types/classes/interfaces
+- `snake_case` for log event names and log field names
+- Prefix interfaces with descriptive nouns (e.g., `EventContext`, `TrackWorkflowRequest`)
 
-### Security
+### Types
 
-- `sanitizeSecrets()` automatically redacts credentials from error messages
-- Never log tokens, API keys, or sensitive data directly
-- Error messages from git operations may contain URLs with tokens - always use `errorWithException()`
+- Strict mode enabled. Define shared types in `src/types.ts`.
+- Use explicit return types for exported functions.
+- Target: ES2024, module resolution: Bundler.
 
-## Error Handling
+### Code Organization
 
-- Use try/catch for async operations
-- Return early on validation failures
-- Use `errorWithException()` for errors - it sanitizes and formats automatically
-- For API handlers: return JSON errors with appropriate HTTP status codes
+- Keep related code together. Do not split across too many files or over-abstract.
+- External API functions stay in their respective files (`github.ts`, `sandbox.ts`, `oidc.ts`).
+- Comments explain "why", not "what". Skip comments for short (<10 line) functions.
+- Prioritize comments for I/O boundaries, external system orchestration, and stateful code.
 
 ## Testing
 
-**IMPORTANT**: Tests must verify actual implementation behavior, not document expected structures.
+Tests run in `@cloudflare/vitest-pool-workers` (Workers environment). Config: `vitest.config.mts`, `test/tsconfig.json`.
+
+Tests must verify actual implementation behavior, not document expected structures.
 
-### Valid Tests
+### Write tests that
 
 - Call actual functions and verify return values
 - Test input parsing, validation, and error handling with real payloads
 - Verify API contract boundaries (request/response formats)
 - Test edge cases and failure modes
 - Use fixtures from `test/fixtures/` for realistic payloads
 
-### Invalid Tests (Do NOT write these)
+### Do NOT write tests that
 
-- Tests that create local objects and verify their own structure
-- String equality checks with hardcoded values unrelated to implementation
-- "Documentation" tests that don't call real functions
-- Tests that stub/mock everything such that no real code paths are tested
+- Create local objects and verify their own structure
+- Use string equality checks with hardcoded values unrelated to implementation
+- Stub/mock everything such that no real code paths are tested
+- Exist purely as documentation
 
-### Test Philosophy
-
-- Bias towards fewer tests, focusing on integration tests
-- Focus on: user input parsing, API validation, crash resistance
-- More tests are NOT better
+Bias towards fewer, focused integration tests. More tests are not better.
 
 ## Conventions
 
 ### Configuration
 
-- Prefer JSONC for config files (see `wrangler.jsonc`, `wrangler.test.jsonc`)
-- Use `.editorconfig` and `oxfmt` for formatting
-
-### Dependencies
-
-- Minimize new dependencies unless necessary
-- Key packages: Hono (routing), Octokit (GitHub API), agents (Durable Objects), ulid
+- Prefer JSONC for config files (see `wrangler.jsonc`, `wrangler.test.jsonc`).
+- Build-time constants (`__VERSION__`, `__COMMIT__`) are injected via wrangler `--define`.
+- Handlebars templates (`*.hbs`) and SQL files (`*.sql`) are imported as strings via wrangler `rules`.
 
 ### API Patterns
 
-- Hono routes grouped by feature (auth, api/github, ask, webhooks)
-- OIDC validation before processing API requests
-- Bearer auth for protected endpoints
-- Return `{ error: string }` for error responses with appropriate status codes
-- Return `{ ok: true }` for success responses
+- Hono routes grouped by feature (auth, api/github, ask, webhooks).
+- OIDC validation before processing API requests from GitHub Actions.
+- Bearer auth for protected endpoints (`ASK_SECRET`).
+- Return `{ error: string }` for errors, `{ ok: true }` for success.
 
 ### GitHub Integration
 
-- Use `createOctokit()` with installation ID for authenticated requests
-- `ResilientOctokit` includes retry and throttling plugins
-- GraphQL for fetching issue/PR context (avoids multiple REST calls)
-- REST for mutations (comments, reactions, PRs)
+- Use `createOctokit()` with installation ID for authenticated requests.
+- `ResilientOctokit` includes retry and throttling plugins.
+- GraphQL for fetching issue/PR context (avoids multiple REST calls). REST for mutations.
+- Installation IDs are cached in KV (`APP_INSTALLATIONS`) with 30-minute TTL.
 
-### Releases
+### Durable Objects
 
-- Ignore changes to `.github/` directories when writing release notes — those are internal workflow configs, not user-facing
+- `RepoAgent`: Tracks workflow runs per repo, posts failure comments. ID format: `{owner}/{repo}`.
+- Three finalization paths: action-driven (finalize.ts), polling (alarm), `workflow_run` webhook (safety net).
+- Uses `agents` package for simplified DO management.
 
-### Durable Objects
+### Releases
 
-- `RepoAgent`: Tracks workflow runs per repo, posts failure comments
-- ID format: `{owner}/{repo}`
-- Uses `agents` package for simplified DO management
+- Ignore changes to `.github/` directories when writing release notes -- those are internal workflow configs, not user-facing.
PATCH

echo "Gold patch applied."
