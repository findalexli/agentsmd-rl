#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sanity

# Idempotency guard
if grep -qF "**Important:** Do NOT use `pnpm test -- path/to/file.test.ts` for running a sing" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -128,8 +128,11 @@ Unit tests run in jsdom with mocks and **do not require any authentication**:
 # Build first (required), then run all tests
 pnpm build && pnpm test
 
-# Run a specific test file
-pnpm test -- packages/sanity/src/core/hooks/useClient.test.ts
+# Run a single test file (IMPORTANT: use vitest directly with --project to avoid running all tests)
+pnpm vitest run --project=sanity packages/sanity/src/core/hooks/useClient.test.ts
+
+# Run a single test file with verbose output
+pnpm vitest run --project=sanity --reporter=verbose packages/sanity/src/core/hooks/useClient.test.ts
 
 # Watch mode for iterative development
 pnpm test -- --watch
@@ -138,6 +141,8 @@ pnpm test -- --watch
 pnpm test -- --project=sanity
 ```
 
+**Important:** Do NOT use `pnpm test -- path/to/file.test.ts` for running a single file — it runs all tests across all projects. Use `pnpm vitest run --project=<project> <path>` instead.
+
 Components that need auth context use `createMockAuthStore` in tests, so no real authentication is needed. This is the recommended way to verify most code changes.
 
 ### Running the Dev Studio (Auth Required)
PATCH

echo "Gold patch applied."
