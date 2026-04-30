#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gitea

# Idempotency guard
if grep -qF "- Run single go tests with `go test -tags 'sqlite sqlite_unlock_notify' -run '^T" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,8 +2,8 @@
 - Run `make fmt` to format `.go` files, and run `make lint-go` to lint them
 - Run `make lint-js` to lint `.ts` files
 - Run `make tidy` after any `go.mod` changes
-- Run single go unit tests with `go test -tags 'sqlite sqlite_unlock_notify' -run '^TestName$' ./modulepath/`
-- Run single go integration tests with `make 'test-sqlite#TestName/Subtest'`
+- Run single go tests with `go test -tags 'sqlite sqlite_unlock_notify' -run '^TestName$' ./modulepath/`
+- Run single js test files with `pnpm exec vitest <path-filter>`
 - Run single playwright e2e test files with `GITEA_TEST_E2E_FLAGS='<filepath>' make test-e2e`
 - Add the current year into the copyright header of new `.go` files
 - Ensure no trailing whitespace in edited files
PATCH

echo "Gold patch applied."
