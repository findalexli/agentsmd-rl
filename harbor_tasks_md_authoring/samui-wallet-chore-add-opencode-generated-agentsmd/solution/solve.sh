#!/usr/bin/env bash
set -euo pipefail

cd /workspace/samui-wallet

# Idempotency guard
if grep -qF "- **Formatting**: Prettier (single quotes, 120 width, no semicolons, trailing co" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,18 @@
+# Agent Guidelines for Samui Wallet
+
+## Commands
+- **Build**: `pnpm build`
+- **Lint**: `pnpm lint` / `pnpm lint:fix`
+- **Type Check**: `pnpm check-types`
+- **Test All**: `pnpm test` / `pnpm test:watch`
+- **Single Test**: `vitest run <path/to/test.ts>`
+- **Format**: `pnpm format` / `pnpm format:check`
+
+## Code Style
+- **TypeScript**: Strict mode, consistent type definitions/imports
+- **Formatting**: Prettier (single quotes, 120 width, no semicolons, trailing commas)
+- **Linting**: ESLint with perfectionist (alphabetical imports/sorting)
+- **Naming**: camelCase variables/functions, PascalCase types
+- **Error Handling**: Use `tryCatch` from `@workspace/core`
+- **Testing**: Vitest globals, jsdom env, ARRANGE/ACT/ASSERT pattern
+- **Imports**: Type imports separate, alphabetical perfectionist sorting
\ No newline at end of file
PATCH

echo "Gold patch applied."
