#!/usr/bin/env bash
set -euo pipefail

cd /workspace/explorer

# Idempotency guard
if grep -qF "- `CONTEXT_OPTIMIZATION.md`, `CACHING.md`, `RATE_LIMITING.md` - Performance and " ".cursor/rules/architect.mdc" && grep -qF "5. If you touch routes/tabs or page metadata, follow `.cursor/skills/aptos-explo" ".cursor/rules/coder.mdc" && grep -qF "# Match `.node-version` (currently Node 24)" ".cursor/rules/cost-cutter.mdc" && grep -qF "The `src/` folder is nearly drained \u2014 only `src/components/IndividualPageContent" ".cursor/rules/modernizer.mdc" && grep -qF "- **E2E**: Playwright (`e2e/smoke.spec.ts`, `playwright.config.ts`). Run with `p" ".cursor/rules/tester.mdc" && grep -qF "- End-to-end smoke tests live in `e2e/` and run with **Playwright** against a `v" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/architect.mdc b/.cursor/rules/architect.mdc
@@ -18,11 +18,15 @@ You are acting as the **Architect** for the Aptos Explorer project.
 ## Key Files to Review
 
 - `app/router.tsx` - Routing architecture
-- `app/routes/` - File-based route definitions
+- `app/routing.tsx` - `Link` / `useNavigate` wrappers that preserve `?network=`
+- `app/routes/` - File-based route definitions (run `pnpm routes:generate` after changes)
 - `app/api/hooks/` - Data fetching patterns (React Query)
 - `app/context/` - State management patterns
+- `app/settings/` - Settings page screen + per-network API key / decompilation opt-in storage
 - `netlify.toml` - Deployment configuration
-- `CONTEXT_OPTIMIZATION.md` - Performance considerations
+- `docs/FEATURES_SPECIFICATION.md` - Canonical feature catalog (`FEAT-*` IDs) — keep in sync
+- `docs/LLM_ACCESS.md` - LLM/SEO contributor reference
+- `CONTEXT_OPTIMIZATION.md`, `CACHING.md`, `RATE_LIMITING.md` - Performance and rate-limit considerations
 
 ## When Planning Features
 
diff --git a/.cursor/rules/coder.mdc b/.cursor/rules/coder.mdc
@@ -27,6 +27,8 @@ You are acting as the **Coder** for the Aptos Explorer project.
 1. Check existing patterns in similar files
 2. Review types in `app/types/` or nearby files
 3. Understand the data flow (React Query hooks in `app/api/hooks/`)
+4. Check `docs/FEATURES_SPECIFICATION.md` for any `FEAT-*` entry your change touches and keep it in sync
+5. If you touch routes/tabs or page metadata, follow `.cursor/skills/aptos-explorer-llm-seo/SKILL.md` (and update `public/llms.txt`, `public/llms-full.txt`, `public/sitemap.xml`, and `app/components/hooks/usePageMetadata.tsx` as needed)
 
 ## Implementation Checklist
 
@@ -67,6 +69,8 @@ Add entries to `CHANGELOG.md` for notable changes.
 
 ```bash
 pnpm fmt              # Format before committing
-pnpm lint             # Check for errors
-pnpm dev              # Test your changes
+pnpm lint             # TypeScript + Biome lint checks
+pnpm test --run       # Vitest single run (CI mode)
+pnpm dev              # Dev server on port 3030
+pnpm ci:verify        # Local CI: routes:generate + lint + test + build
 ```
diff --git a/.cursor/rules/cost-cutter.mdc b/.cursor/rules/cost-cutter.mdc
@@ -60,7 +60,8 @@ You are acting as the **Cost Cutter** for the Aptos Explorer project, focused on
 ### Faster Builds
 ```toml
 [build.environment]
-  NODE_VERSION = "20"
+  # Match `.node-version` (currently Node 24)
+  NODE_VERSION = "24"
   # Enable build caching
   NETLIFY_USE_YARN = "false"
   NPM_FLAGS = "--prefer-offline"
diff --git a/.cursor/rules/modernizer.mdc b/.cursor/rules/modernizer.mdc
@@ -23,8 +23,8 @@ You are acting as the **Modernizer** for the Aptos Explorer project.
 - Plan major version upgrades carefully
 
 ### 2. Legacy Migration
-The `src/` folder contains legacy code that should migrate to `app/`:
-- `src/components/` → `app/components/`
+The `src/` folder is nearly drained — only `src/components/IndividualPageContent` remains. Finishing this migration retires `src/`:
+- `src/components/IndividualPageContent` → `app/components/`
 - Update imports to use new patterns
 - Adopt React Query hooks from `app/api/hooks/`
 
@@ -103,7 +103,7 @@ pnpm add pkg@latest   # Update to latest
 ## Current Technical Debt
 
 Review these areas for modernization opportunities:
-- `src/components/` - Legacy components
+- `src/components/IndividualPageContent` — last legacy component blocking removal of `src/`
 - Any `// TODO` or `// FIXME` comments
 - Files with `any` type usage
 - Old React patterns (class components, legacy lifecycle)
diff --git a/.cursor/rules/tester.mdc b/.cursor/rules/tester.mdc
@@ -17,9 +17,9 @@ You are acting as the **Tester** for the Aptos Explorer project.
 
 ## Testing Stack
 
-- **Unit/Component**: Vitest + React Testing Library
-- **E2E**: Playwright (if configured)
-- **Visual**: Chromatic or similar
+- **Unit/Component**: Vitest + React Testing Library (`*.test.ts(x)` next to the implementation, run via `pnpm test`).
+- **E2E**: Playwright (`e2e/smoke.spec.ts`, `playwright.config.ts`). Run with `pnpm test:e2e` against a `vite preview` build (port 4173). One-time setup: `pnpm test:e2e:install` to install Chromium + system deps. CI runs Playwright after `pnpm ci:verify`.
+- **Visual**: Chromatic or similar (not yet wired up).
 
 ## Test File Conventions
 
@@ -88,10 +88,12 @@ describe("useAccountData", () => {
 ## Commands
 
 ```bash
-pnpm test              # Watch mode
-pnpm test --run        # Single run (CI)
-pnpm test <pattern>    # Run matching tests
-pnpm test --coverage   # With coverage report
+pnpm test                # Watch mode (Vitest)
+pnpm test --run          # Single run (CI mode)
+pnpm test <pattern>      # Run matching tests
+pnpm test --coverage     # With coverage report
+pnpm test:e2e            # Playwright smoke tests (vite preview on :4173)
+pnpm test:e2e:install    # One-time: install Chromium + system deps
 ```
 
 ## What to Test
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,16 +6,19 @@ This document serves as the canonical source of truth for AI coding assistants w
 
 ```bash
 # Node: see `.node-version` (matches CI via actions/setup-node node-version-file)
-pnpm install          # Install dependencies
-pnpm routes:generate  # TanStack route tree (also runs before dev/build/lint/test via pre* scripts)
-pnpm dev              # Dev server on port 3030
-pnpm start            # Dev server on port 3000
-pnpm build            # Production build
-pnpm ci:verify        # Local CI: generate routes, lint, test, production build
-pnpm test             # Run Vitest
-pnpm lint             # TypeScript + Biome lint checks
-pnpm fmt              # Apply Biome formatting
-pnpm check            # Biome lint + format + organize imports
+pnpm install            # Install dependencies
+pnpm routes:generate    # TanStack route tree (also runs before dev/build/lint/test via pre* scripts)
+pnpm dev                # Dev server on port 3030
+pnpm start              # Dev server on port 3000
+pnpm build              # Production build
+pnpm ci:verify          # Local CI: generate routes, lint, test, production build
+pnpm test               # Run Vitest (watch mode)
+pnpm test --run         # Vitest single run (CI mode)
+pnpm test:e2e           # Playwright smoke tests against `vite preview` (port 4173)
+pnpm test:e2e:install   # Install Playwright Chromium browser + system deps
+pnpm lint               # TypeScript + Biome lint checks
+pnpm fmt                # Apply Biome formatting
+pnpm check              # Biome lint + format + organize imports
 ```
 
 **Before committing**: Always run `pnpm fmt && pnpm lint` to ensure code quality.
@@ -27,19 +30,29 @@ pnpm check            # Biome lint + format + organize imports
 ```
 explorer/
 ├── app/                    # TanStack Start application
-│   ├── routes/             # File-based routing
-│   ├── components/         # Shared UI components
-│   ├── api/hooks/          # React Query data hooks
+│   ├── routes/             # File-based routing (TanStack Router)
+│   ├── components/         # Shared UI components (incl. `components/hooks/`)
+│   ├── api/                # Aptos clients + React Query hooks (`api/hooks/`)
 │   ├── context/            # React context providers
-│   ├── pages/              # Page components
-│   ├── utils/              # Utility functions
+│   ├── pages/              # Page-level screens used by route components
+│   ├── settings/           # Settings page screen + storage utilities
+│   ├── data/               # Per-network static data (known addresses, branding)
+│   ├── hooks/              # App-wide hooks not tied to data fetching
+│   ├── lib/                # Cross-cutting helpers (e.g. wallet, Decibel parsers)
+│   ├── utils/              # Utility functions (incl. drift tests)
 │   ├── types/              # Shared TypeScript types
-│   └── themes/             # Theme configuration
-├── src/                    # Legacy/compat code (prefer app/)
-├── public/                 # Static assets
+│   ├── themes/             # MUI theme configuration
+│   ├── wasm/               # Move decompiler / disassembler WASM bindings
+│   └── global-config/      # Static runtime configuration
+├── src/                    # Legacy/compat code (prefer app/) — only `IndividualPageContent` remains
+├── public/                 # Static assets, `llms*.txt`, `sitemap.xml`, `robots.txt`
 ├── analytics/              # SQL analytics queries
-├── .agents/                # Task management (Kanban)
-├── .cursor/                # Cursor IDE configuration
+├── docs/                   # Contributor docs (`FEATURES_SPECIFICATION.md`, `LLM_ACCESS.md`)
+├── e2e/                    # Playwright smoke tests (`smoke.spec.ts`)
+├── scripts/                # One-off shell scripts (e.g. `generate-icons.sh`)
+├── typings/                # Ambient type declarations
+├── .agents/                # Task management (Kanban) and issue tracker
+├── .cursor/                # Cursor IDE configuration (rules, notepads, skills)
 ├── .agent/                 # Antigravity rules
 ├── .vibe/                  # Mistral Vibe agents
 ├── .opencode/              # OpenCode agents
@@ -118,6 +131,8 @@ This repository is often modified by automated agents. The following bar keeps t
 ### Tests and mocks
 
 - **Do not call real Aptos APIs** from unit tests; mock at the hook or fetch layer. Prefer behavioral assertions over snapshot noise.
+- Unit tests live next to the implementation as `*.test.ts(x)` and run with **Vitest**. The `pretest` script regenerates the route tree first.
+- End-to-end smoke tests live in `e2e/` and run with **Playwright** against a `vite preview` build (`pnpm test:e2e`). The `e2e/**` glob is excluded from Vitest. CI runs Playwright after `pnpm ci:verify` and maps each `APTOS_<NETWORK>_API_KEY` repository secret to both `VITE_APTOS_<NETWORK>_API_KEY` (client bundle) and `APTOS_<NETWORK>_API_KEY` (SSR) so client and server share one identity.
 
 ### Features Specification and regression prevention
 
@@ -348,7 +363,7 @@ pnpm test <pattern>    # Run specific tests
 - React, TanStack Router/Query version updates
 - Vite and build tooling upgrades
 - TypeScript strict mode improvements
-- Legacy component migration from `src/components/`
+- Legacy component migration from `src/components/` (only `IndividualPageContent` remains — finishing this migration retires `src/`)
 
 **Outputs**: Migration PRs, upgrade guides, deprecation removal
 
@@ -416,15 +431,28 @@ chore(deps): update tanstack-query to v5
 
 ## Environment Configuration
 
-Copy `.env.local` to `.env` and configure:
+Copy `.env.example` to `.env.local` and uncomment the variables you need. Common overrides:
 
 ```bash
-VITE_API_URL=...           # Aptos API endpoint
-VITE_GRAPHQL_URL=...       # GraphQL endpoint
-# Add other VITE_* or REACT_APP_* variables as needed
+# Per-network Aptos API Gateway keys (client bundle).
+# VITE_APTOS_MAINNET_API_KEY=AG-...
+# VITE_APTOS_TESTNET_API_KEY=AG-...
+# VITE_APTOS_DEVNET_API_KEY=AG-...
+
+# Per-network Aptos API Gateway keys (SSR / server). Set the same value as the
+# matching VITE_* variable so the browser and server share one identity.
+# APTOS_MAINNET_API_KEY=AG-...
+# APTOS_TESTNET_API_KEY=AG-...
+
+# Optional custom endpoints / analytics.
+# APTOS_DEVNET_URL=https://api.devnet.staging.aptoslabs.com/v1
+# REACT_APP_GTM_ID=GTM-XXXXXXX
+
+# Feature tier banner — also overridable at runtime via the `feature_name` cookie.
+# VITE_FEATURE_NAME=prod   # values: prod | dev | earlydev
 ```
 
-**Never commit secrets** - use runtime environment variables.
+Vite exposes variables prefixed with `VITE_` (and `REACT_APP_` for compatibility) to the client bundle; everything else is server-only. Users can also set per-network API keys at runtime via **Settings** (`/settings`). **Never commit secrets** — use runtime environment variables.
 
 ---
 
PATCH

echo "Gold patch applied."
