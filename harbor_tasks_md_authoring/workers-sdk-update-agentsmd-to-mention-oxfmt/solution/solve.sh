#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotency guard
if grep -qF "- Format with oxfmt - run `pnpm prettify` in the workspace root before committin" "AGENTS.md" && grep -qF "packages/create-cloudflare/AGENTS.md" "packages/create-cloudflare/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -96,14 +96,14 @@ This is the **Cloudflare Workers SDK** monorepo containing tools and libraries f
 - Use `node:` prefix for Node.js imports (`import/enforce-node-protocol-usage`)
 - Prefix unused variables with `_`
 - No `.only()` in tests (`no-only-tests/no-only-tests`)
-- Format with Prettier - run `pnpm prettify` in the workspace root before committing
+- Format with oxfmt - run `pnpm prettify` in the workspace root before committing
 - All changes to published packages require a changeset (see below)
 
-**Formatting (Prettier):**
+**Formatting (oxfmt):**
 
 - Tabs (not spaces), double quotes, semicolons, trailing commas (es5)
 - Import order enforced: builtins → third-party → parent → sibling → index → types
-- `prettier-plugin-packagejson` sorts package.json keys
+- `sortPackageJson` option sorts package.json keys
 
 **Security:**
 
diff --git a/packages/create-cloudflare/AGENTS.md b/packages/create-cloudflare/AGENTS.md
@@ -19,7 +19,6 @@ Project scaffolding CLI for Cloudflare Workers. Single entry: `src/cli.ts` serve
 ## CONVENTIONS
 
 - `no-console: error` — use project's logging utilities
-- Own `.prettierrc` — same settings as root but without `prettier-plugin-packagejson`
 - Templates excluded from linting (except `c3.ts` files within templates)
 - Templates excluded from formatting (except hello-world templates)
 
PATCH

echo "Gold patch applied."
