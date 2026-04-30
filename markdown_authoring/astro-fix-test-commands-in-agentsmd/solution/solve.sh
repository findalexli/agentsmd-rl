#!/usr/bin/env bash
set -euo pipefail

cd /workspace/astro

# Idempotency guard
if grep -qF "- For focused Astro package runs: `pnpm -C packages/astro test:unit`, `pnpm -C p" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -37,18 +37,12 @@ Note: Edits to source files take effect after rebuilding the package via `pnpm b
 
 # Running Tests
 
-- Run `pnpm test` in workspace root or package directory to run full test suite (can be slow!)
-- Integration tests live in special `packages/integrations` folders.
-- Example: `pnpm -C <package-directory> astro-scripts test` - Run a single package test suite
-- Example: `pnpm -C <package-directory> astro-scripts test "test/actions.test.js"` - Run a single test file
-- Example: `pnpm -C <package-directory> astro-scripts test "test/**/*.test.js" --match "CSS"` - Run specific tests matching a string or regex patterns
-- Example: `pnpm -C <package-directory> astro-scripts test "test/{actions,css,middleware}.test.js"` - Run multiple test files
-- Key flags:
-  - `--match` / `-m`: Filter tests by name pattern (regex)
-  - `--only` / `-o`: Run only tests marked with `.only`
-  - `--parallel` / `-p`: Run tests in parallel (default is sequential)
-  - `--timeout` / `-t`: Set timeout in milliseconds
-  - `--watch` / `-w`: Watch mode
+- Run `pnpm test` in the workspace root to run the full suite (slow).
+- Run `pnpm -C <package-directory> test` to run a package’s tests (example: `pnpm -C packages/astro test`, `pnpm -C packages/integrations/react test`).
+- Run an individual test file with `node path/to/test.js` (non-E2E).
+- For focused Astro package runs: `pnpm -C packages/astro test:unit`, `pnpm -C packages/astro test:integration`, `pnpm -C packages/astro test:cli`, `pnpm -C packages/astro test:types`.
+- For matching a subset by test name in Astro: `pnpm -C packages/astro test:match -- "<pattern>"`.
+- For E2E: `pnpm test:e2e` or `pnpm test:e2e:match -- "<pattern>"`.
 
 # Astro Quick Reference
 
PATCH

echo "Gold patch applied."
