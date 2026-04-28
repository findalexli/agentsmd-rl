#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rsbuild

# Idempotency guard
if grep -qF "This monorepo contains the Rsbuild build tool, plugins, and related packages. Rs" ".github/copilot-instructions.md" && grep -qF "This monorepo contains the Rsbuild build tool, plugins, and related packages. Rs" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,10 +1,10 @@
-# Rsbuild - High-Performance Rspack-based Build Tool
+# Rsbuild
 
-Rsbuild is a monorepo containing the core Rsbuild build tool, plugins, and related packages. It's a high-performance build tool powered by Rspack with TypeScript, JavaScript, React, Vue, and other framework support.
+This monorepo contains the Rsbuild build tool, plugins, and related packages. Rsbuild is a high-performance JavaScript build tool powered by Rspack.
 
 ## Setup & Build
 
-**Setup (NEVER CANCEL - takes 2+ minutes):**
+**Setup (NEVER CANCEL):**
 
 ```bash
 npm install corepack@latest -g && corepack enable
@@ -23,13 +23,13 @@ npx nx build @rsbuild/core    # Specific package
 **Testing:**
 
 ```bash
-pnpm test                     # Unit tests (~10s)
-pnpm e2e                      # E2E tests (~60s)
-pnpm lint                     # Lint code (~5s) - REQUIRED before finishing
+pnpm test                     # Unit tests
+pnpm e2e                      # E2E tests
+pnpm lint                     # Lint code - REQUIRED before finishing
 pnpm format                   # Format code
 ```
 
-**E2E tests (NEVER CANCEL - takes 10+ minutes):**
+**E2E tests (NEVER CANCEL):**
 
 ```bash
 cd e2e && pnpm install && npx playwright install chromium
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,21 @@
+# AGENTS.md
+
+This monorepo contains the Rsbuild build tool, plugins, and related packages. Rsbuild is a high-performance JavaScript build tool powered by Rspack.
+
+## Commands
+
+- **Build**: `pnpm build` (all packages) | `npx nx build @rsbuild/core` (specific)
+- **Test**: `pnpm test` (unit tests) | `pnpm test:watch` (watch mode) | `pnpm e2e` (E2E tests)
+- **Single test**: `pnpm test packages/core/src/foo.test.ts` (unit test) | `pnpm e2e:rspack cli/base/index.test.ts` (E2E test)
+- **Lint**: `pnpm lint` (REQUIRED before commits) | `pnpm format` (format code)
+
+## Code style
+
+- **Formatting**: Single quotes, Prettier
+- **Types**: TypeScript strict mode
+- **Naming**: camelCase files/functions, PascalCase components/classes, kebab-case packages
+
+## Architecture
+
+- **Structure**: Monorepo with `packages/core/` (main), `packages/plugin-*/` (plugins)
+- **Testing**: `.test.ts` files, use `rstest` runner
PATCH

echo "Gold patch applied."
