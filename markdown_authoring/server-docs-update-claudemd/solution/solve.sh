#!/usr/bin/env bash
set -euo pipefail

cd /workspace/server

# Idempotency guard
if grep -qF "- Use TDD by default: write a failing test, verify it fails for the right reason" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,31 +2,39 @@
 
 ## Git
 
-Use conventional commit prefixes for all commits (e.g. fix:, feat:, chore:, refactor:, test:, docs:).
-Suggest a branch name before starting any code changes.
+- Use conventional commit prefixes (e.g. fix:, feat:, chore:, refactor:, test:, docs:)
+- Suggest a branch name before starting any code changes
 
 ## General
 
-Ask me before trying to start the server.
-
-Keep code simple and readable. Don't remove duplication too early. Don't over-optimize for code that is "convenient" to change — we want it to be simple to understand.
-
-Do not add comments. Use meaningful names for variables and functions instead.
-
-After completing a request, check if any extra unnecessary code has been added, and remove it.
+- Ask before starting the server
+- Prefer simple and obvious — do not deduplicate until a pattern has appeared at least three times
+- Do not add comments — use meaningful names instead
+- Before considering a task done, remove any scaffolding, debug logs, or temporary code added during implementation
 
 ## Commands
 
-Use `npm run test` scoped to the current test file. If test output is truncated, rerun without coverage for full output. When tests fail, provide the specific error message.
+- Run tests with `pnpm test` scoped to the current test file
+- If test output is truncated, rerun without coverage for full output
+- When tests fail, provide the specific error message
 
 ## Process
 
-Use TDD: write a failing test, verify it fails for the expected reason with a clear error message, pass it in the simplest way, then refactor. Prefer outside-in testing. If asked to implement without a test, ask if it should be tested.
+- Use TDD by default: write a failing test, verify it fails for the right reason, pass it in the simplest way, then refactor. If asked to implement without a test, confirm whether to skip it.
+- Prefer outside-in testing
+- Only mock external dependencies (HTTP calls, third-party APIs, email) — not internal services
+- A passing test suite is not proof of correctness — before committing, review affected user flows in the codebase to check for regressions
 
 ## Architecture
 
-Handlers deal with HTTP requests or event logic, not business logic. Commands deal with business logic and should not directly access the database.
+- Handlers deal with HTTP requests or event logic, not business logic
+- Use cases in `src/usecases/` deal with business logic and must not directly access the database
+- Services receive repository interfaces via their constructor — never import the database inside a service
 
 ## Security
 
-Always use parameterized queries with Knex — never use `knex.raw()` with string concatenation. Validate and sanitize all user input at the handler level. Never log sensitive data (passwords, tokens, personal information). Use `res.locals` for passing authenticated user data through middleware.
+- IMPORTANT: Use `== null` to check for absent values — not `!value`, which incorrectly rejects falsy IDs like `0`
+- Never use `knex.raw()` with string concatenation — always use parameterized queries
+- Validate and sanitize all user input at the handler level
+- Never log sensitive data (passwords, tokens, personal information)
+- Use `res.locals` for passing authenticated user data through middleware
PATCH

echo "Gold patch applied."
