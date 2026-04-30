#!/usr/bin/env bash
set -euo pipefail

cd /workspace/llmgateway

# Idempotency guard
if grep -qF "When running curl commands against the local API, you can use `test-token` as au" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -29,6 +29,8 @@ Always run `pnpm format` before committing code. Run `pnpm generate` if API rout
 - `pnpm test:unit` - Run unit tests (\*.spec.ts files)
 - `pnpm test:e2e` - Run end-to-end tests (\*.e2e.ts files)
 
+When running curl commands against the local API, you can use `test-token` as authentication.
+
 #### E2E Test Options
 
 - `TEST_MODELS` - Run tests only for specific models (comma-separated list of `provider/model-id` pairs)
PATCH

echo "Gold patch applied."
