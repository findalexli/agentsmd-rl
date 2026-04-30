#!/usr/bin/env bash
set -euo pipefail

cd /workspace/backstage

# Idempotency guard
if grep -qF "- Test: Use `yarn test --no-watch <path>` in the project root to run tests. The " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -14,7 +14,7 @@ The following files contain guidelines for the project:
 Before any of these commands can be run, you need to run `yarn install` in the project root.
 
 - Build: There is no need to build the project during development, and it is verified automatically in the CI pipeline.
-- Test: Use `yarn test <path>` in the project root to run tests. The path can be either a single file or a directory, and be omitted to run tests for all changed files.
+- Test: Use `yarn test --no-watch <path>` in the project root to run tests. The path can be either a single file or a directory. Always provide a path, avoid running all tests.
 - Type checking: Use `yarn tsc` in the project root to run the type checker.
 - Code formatting: Use `yarn prettier --write <path>` to format code.
 - Lint: Use `yarn lint --fix` in the project root to run the linter.
PATCH

echo "Gold patch applied."
