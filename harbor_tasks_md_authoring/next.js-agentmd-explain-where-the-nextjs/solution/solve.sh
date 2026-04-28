#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency guard
if grep -qF "The main Next.js framework lives in `packages/next/`. This is what gets publishe" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,5 +1,44 @@
 # Next.js Development Guide
 
+## Codebase structure
+
+### Monorepo Overview
+
+This is a pnpm monorepo containing the Next.js framework and related packages.
+
+```
+next.js/
+├── packages/           # Published npm packages
+├── turbopack/          # Turbopack bundler (Rust) - git subtree
+├── crates/             # Rust crates for Next.js SWC bindings
+├── test/               # All test suites
+├── examples/           # Example Next.js applications
+├── docs/               # Documentation
+└── scripts/            # Build and maintenance scripts
+```
+
+### Core Package: `packages/next`
+
+The main Next.js framework lives in `packages/next/`. This is what gets published as the `next` npm package.
+
+**Source code** is in `packages/next/src/`.
+
+**Key entry points:**
+
+- Dev server: `src/cli/next-dev.ts` → `src/server/dev/next-dev-server.ts`
+- Production server: `src/cli/next-start.ts` → `src/server/next-server.ts`
+- Build: `src/cli/next-build.ts` → `src/build/index.ts`
+
+**Compiled output** goes to `packages/next/dist/` (mirrors src/ structure).
+
+### Other Important Packages
+
+- `packages/create-next-app/` - The `create-next-app` CLI tool
+- `packages/next-swc/` - Native Rust bindings (SWC transforms)
+- `packages/eslint-plugin-next/` - ESLint rules for Next.js
+- `packages/font/` - `next/font` implementation
+- `packages/third-parties/` - Third-party script integrations
+
 ## Git Workflow
 
 **Use Graphite for all git operations** instead of raw git commands:
@@ -221,19 +260,18 @@ pnpm test-dev-turbo test/path/to/test.ts
 pnpm test-start-turbo test/path/to/test.ts
 ```
 
-## Key Directories
+## Key Directories (Quick Reference)
+
+See [Codebase structure](#codebase-structure) above for detailed explanations.
 
 - `packages/next/src/` - Main Next.js source code
-  - `server/` - Server runtime (dev server, router, rendering)
-  - `client/` - Client-side code
-  - `build/` - Build tooling (webpack, turbopack configs)
-  - `cli/` - CLI entry points
-- `packages/next/dist/` - Compiled output
-- `turbopack/` - Turbopack bundler (Rust)
-- `test/` - Test suites
-  - `development/` - Dev server tests
-  - `production/` - Production build tests
-  - `e2e/` - End-to-end tests
+- `packages/next/src/server/` - Server runtime (most changes happen here)
+- `packages/next/src/client/` - Client-side runtime
+- `packages/next/src/build/` - Build tooling
+- `test/e2e/` - End-to-end tests
+- `test/development/` - Dev server tests
+- `test/production/` - Production build tests
+- `test/unit/` - Unit tests (fast, no browser)
 
 ## Development Tips
 
PATCH

echo "Gold patch applied."
