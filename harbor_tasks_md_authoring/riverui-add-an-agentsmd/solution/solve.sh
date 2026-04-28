#!/usr/bin/env bash
set -euo pipefail

cd /workspace/riverui

# Idempotency guard
if grep -qF "- Tests: `npm run test`, `npm run test:once`, `npm exec -- vitest --run path/to/" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,23 @@
+# River UI Agent Guidelines
+
+## Commands
+- Dev: `npm run dev` (pro: `npm run dev:pro`)
+- Lint/format: `npm run lint`, `npm run fmt`
+- Tests: `npm run test`, `npm run test:once`, `npm exec -- vitest --run path/to/file.test.tsx`
+- Build: `npm run build`, `make build`
+- Go lint/test: `make lint`, `make test`
+
+## Rules
+- No `any`; use `unknown` or specific types.
+- Tests live beside components (`.test.tsx`).
+- Prefix unused variables with `_`.
+
+## Validate
+- UI/router/search-state: targeted tests + `npm run lint`.
+- Larger changes: `npm run test:once` + `npm run build`.
+- Go changes: `make lint`.
+
+## Commits
+- Title <= 50 chars (max 72); wrap body ~72.
+- Explain problem, fix, why it works, and tests.
+- Use auto-close keywords; don’t mention "ran lint/tests".
PATCH

echo "Gold patch applied."
