#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotency guard
if grep -qF "When making architectural changes to a package (renaming files, adding entry poi" "AGENTS.md" && grep -qF "- `src/workers/local-explorer/openapi.local.json` \u2014 generated from `scripts/open" "packages/miniflare/AGENTS.md" && grep -qF "- When adding `expect` as a parameter to helper functions, check ALL call sites " "packages/wrangler/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -96,6 +96,9 @@ This is the **Cloudflare Workers SDK** monorepo containing tools and libraries f
 - Use `node:` prefix for Node.js imports (`import/enforce-node-protocol-usage`)
 - Prefix unused variables with `_`
 - No `.only()` in tests (`no-only-tests/no-only-tests`)
+- Prefer `function` declarations over `const` arrow function assignments for named/exported functions
+- ESLint disable comments must use double-dash separator: `// eslint-disable-next-line rule-name -- reason here`
+- Never modify generated files directly — modify the generator or config, then regenerate
 - Format with oxfmt - run `pnpm prettify` in the workspace root before committing
 - All changes to published packages require a changeset (see below)
 
@@ -122,6 +125,15 @@ This is the **Cloudflare Workers SDK** monorepo containing tools and libraries f
 - Use `vitest-pool-workers` for testing actual Workers runtime behavior
 - Shared vitest config (`vitest.shared.ts`): 50s timeouts, `retry: 2`, `restoreMocks: true`
 - Vitest 4 pool config: use `maxWorkers: 1` instead of the removed `poolOptions.forks.singleFork: true` when tests must run sequentially
+- **`expect` must come from test context** — never `import { expect } from "vitest"`:
+  - Use destructured test context: `it("name", ({ expect }) => { ... })`
+  - For helper functions that need `expect`, pass it as a parameter with type `ExpectStatic`
+  - Always use `import type` for `ExpectStatic`: `import { beforeAll, type ExpectStatic, test } from "vitest"`
+  - When test context is unavailable (e.g. setup files), use `node:assert` instead
+  - E2E vitest configs do NOT set `globals: true` — this rule is critical there; forgetting `{ expect }` in the callback causes `ReferenceError` at runtime
+- When changing user-facing strings or output messages, update corresponding test snapshots
+- New test fixtures in `vitest-pool-workers-examples/` must include a `tsconfig.json`
+- Test fixtures serve as user-facing recipes — use clean patterns, avoid type casting where possible
 
 **Git Workflow:**
 
@@ -173,6 +185,7 @@ start with a capital letter and describe the change directly (e.g., "Remove unus
 - No h1/h2/h3 headers in changeset descriptions (changelog uses h3)
 - Config examples must use `wrangler.json` (JSONC), not `wrangler.toml`
 - Separate changesets for distinct changes; do not lump unrelated changes
+- Focus on user-facing impact; reference the public-facing package, not internal implementation packages
 
 ## Anti-Patterns
 
@@ -188,6 +201,8 @@ These are explicitly forbidden across the repo:
 - **Named imports from `ci-info`** → use default import (`import ci from "ci-info"`)
 - **Runtime dependencies** → bundle deps; external deps need explicit allowlist entry
 - **Committing to main** → always work on a branch
+- **Trivial/obvious code comments** → don't add comments that restate what the code does; comments should explain "why", not "what"
+- **Duplicating types/constants across packages** → export from the owning package and import where needed
 
 ## Subdirectory Knowledge
 
@@ -199,3 +214,5 @@ Packages with their own AGENTS.md for deeper context:
 - `packages/create-cloudflare/AGENTS.md` - Scaffolding, template system
 - `packages/vitest-pool-workers/AGENTS.md` - 3-context architecture, cloudflare:test module
 - `packages/workers-utils/AGENTS.md` - Shared config validation, test helpers
+
+When making architectural changes to a package (renaming files, adding entry points, changing build output), update the relevant AGENTS.md to reflect the new structure.
diff --git a/packages/miniflare/AGENTS.md b/packages/miniflare/AGENTS.md
@@ -46,6 +46,11 @@ Local dev simulator for Cloudflare Workers, powered by workerd runtime. Main cla
 - `useServer()` — temp HTTP server with auto-cleanup
 - `TestLog` — captures log entries by level
 
+## Generated Files
+
+- `src/runtime/config/generated/workerd.ts` — generated Cap'n Proto types, do not edit directly
+- `src/workers/local-explorer/openapi.local.json` — generated from `scripts/openapi-filter-config.ts`, modify the config not the output
+
 ## Version Pinning
 
 - Miniflare minor version must match workerd minor version
diff --git a/packages/wrangler/AGENTS.md b/packages/wrangler/AGENTS.md
@@ -46,5 +46,6 @@ Main CLI for Cloudflare Workers. ~2k-line yargs command tree in `src/index.ts`.
 
 ## Anti-Patterns
 
-- Never import `expect` from vitest — use test context `({ expect }) => {}`
 - Test files use `.test.ts` (not `.spec.ts`)
+- Never import `expect` from vitest — use test context `({ expect }) => {}`
+  - When adding `expect` as a parameter to helper functions, check ALL call sites (e.g., across `deployments.test.ts`, `versions.test.ts`)
PATCH

echo "Gold patch applied."
