#!/usr/bin/env bash
set -euo pipefail

cd /workspace/devtools

# Idempotency guard
if grep -qF "- **Client context**: webcomponents/Nuxt UI state (`packages/core/src/client/web" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,73 +1,71 @@
 # AGENTS GUIDE
 
-Quick reference for future agents working on this repo.
-
 ## Stack & Structure
-- Monorepo via `pnpm` workspaces; builds orchestrated with `turbo`.
-- ESM TypeScript everywhere; bundling with `tsdown`.
-- Key packages:
-  - `packages/core` (`@vitejs/devtools`): Vite plugin, CLI, host/runtime (docks, views, terminals), websocket RPC server, standalone/webcomponents client.
-  - `packages/kit` (`@vitejs/devtools-kit`): public types/utilities (`defineRpcFunction`, shared state, events) for integration authors; client helpers.
-  - `packages/rpc` (`@vitejs/devtools-rpc`): thin typed RPC wrapper over `birpc`, with WS presets.
-  - `packages/rolldown` (`@vitejs/devtools-rolldown`): Nuxt-based UI served from the plugin; registers Vite dock and RPC functions for Rolldown build data.
-  - `packages/webext`: browser extension scaffolding (currently ancillary).
-- Docs under `docs/` (VitePress); user-facing guides in `docs/guide`.
-- Path aliases defined in `alias.ts` and propagated to `tsconfig.base.json` (do not edit paths manually).
+
+Monorepo (`pnpm` workspaces + `turbo`). ESM TypeScript; bundled with `tsdown`. Path aliases in `alias.ts` (propagated to `tsconfig.base.json` — do not edit manually).
+
+### Packages
+
+| Package | npm | Description |
+|---------|-----|-------------|
+| `packages/core` | `@vitejs/devtools` | Vite plugin, CLI, runtime hosts (docks, views, terminals), WS RPC server, standalone/webcomponents client |
+| `packages/kit` | `@vitejs/devtools-kit` | Public types/utilities for integration authors (`defineRpcFunction`, shared state, events, client helpers) |
+| `packages/rpc` | `@vitejs/devtools-rpc` | Typed RPC wrapper over `birpc` with WS presets |
+| `packages/ui` | `@vitejs/devtools-ui` | Shared UI components, composables, and UnoCSS preset (`presetDevToolsUI`). Private, not published |
+| `packages/rolldown` | `@vitejs/devtools-rolldown` | Nuxt UI for Rolldown build data. Serves at `/.devtools-rolldown/` |
+| `packages/vite` | `@vitejs/devtools-vite` | Nuxt UI for Vite DevTools (WIP). Serves at `/.devtools-vite/` |
+| `packages/self-inspect` | `@vitejs/devtools-self-inspect` | Meta-introspection — DevTools for the DevTools. Serves at `/.devtools-self-inspect/` |
+| `packages/webext` | — | Browser extension scaffolding (ancillary) |
+
+Other top-level directories:
+- `docs/` — VitePress docs; guides in `docs/guide/`
+- `skills/` — Agent skill files generated from docs via [Agent Skills](https://agentskills.io/home). Structured references (RPC patterns, dock types, shared state, project structure) for AI agent context.
 
 ```mermaid
 flowchart TD
-  core["@vitejs/devtools"] --> kit["@vitejs/devtools-kit"]
-  core --> rpc["@vitejs/devtools-rpc"]
-  core --> rolldownUI["@vitejs/devtools-rolldown (Nuxt UI)"]
-  rolldownUI --> kit
-  rolldownUI --> rpc
-  webext["@vitejs/devtools-webext"] --> core
+  core["core"] --> kit & rpc
+  core --> rolldown & vite & self-inspect
+  rolldown --> kit & rpc & ui
+  vite --> kit & rpc & ui
+  self-inspect --> kit & rpc
+  webext --> core
 ```
 
-## Runtime Architecture (high level)
-- Plugin entry (`createDevToolsContext` in `packages/core/src/node/context.ts`) builds a `DevToolsNodeContext` with hosts for RPC, docks, views, terminals. It registers built-in RPC functions and invokes `plugin.devtools.setup` hooks from Vite plugins.
-- Node context vs client context:
-  - **Node context**: server-side state (cwd, workspaceRoot, vite config, mode, rpc/docks/views/terminals hosts) plus internal storage (auth) from `context-internal.ts`. Used by plugins and RPC handlers.
-  - **Client context**: webcomponents/Nuxt UI state (`packages/core/src/client/webcomponents/state/*`), holding dock entries, selected panels, and RPC client; created with `clientType` of `embedded` or `standalone`.
-- Websocket server (`packages/core/src/node/ws.ts`) exposes RPC via `@vitejs/devtools-rpc/presets/ws`. Auth is skipped in build mode or when `devtools.clientAuth` is `false`; trusted IDs stored under `node_modules/.vite/devtools/auth.json`.
-- DevTools middleware (`packages/core/src/node/server.ts`) serves connection meta and standalone client assets.
-- The Rolldown UI plugin (`packages/rolldown/src/node/plugin.ts`) registers RPC functions (Rolldown data fetchers) and hosts the Nuxt-generated static UI at `/.devtools-rolldown/`, adding a dock entry.
-- Nuxt app config (`packages/rolldown/src/nuxt.config.ts`): SPA, base `/.devtools-rolldown/`, disables Nuxt devtools, enables typed pages, uses Unocss/VueUse; sets `vite.devtools.clientAuth = false` for UI.
+## Architecture
 
-## Client Modes (kit/core)
-- **Embedded mode**: default overlay injected into the host app; docks render inside the app shell; use `clientType: 'embedded'` when creating client context.
-- **Standalone mode**: runs the webcomponents UI as an independent page (see `packages/core/src/client/standalone`); useful for external access or when not injecting into the host app UI.
+- **Entry**: `createDevToolsContext` (`packages/core/src/node/context.ts`) builds `DevToolsNodeContext` with hosts for RPC, docks, views, terminals. Invokes `plugin.devtools.setup` hooks.
+- **Node context**: server-side (cwd, vite config, mode, hosts, auth storage at `node_modules/.vite/devtools/auth.json`).
+- **Client context**: webcomponents/Nuxt UI state (`packages/core/src/client/webcomponents/state/*`) — dock entries, panels, RPC client. Two modes: `embedded` (overlay in host app) and `standalone` (independent page).
+- **WS server** (`packages/core/src/node/ws.ts`): RPC via `@vitejs/devtools-rpc/presets/ws`. Auth skipped in build mode or when `devtools.clientAuth` is `false`.
+- **Nuxt UI plugins** (rolldown, vite, self-inspect): each registers RPC functions and hosts static Nuxt SPA at its own base path.
 
-## Development Workflow
-- Install: `pnpm install` (repo requires `pnpm@10.x`).
-- Build all: `pnpm build` (runs `turbo run build`; for UI data, build generates Rolldown metadata under `packages/rolldown/node_modules/.rolldown`).
-- Dev:
-  - Core playground: `pnpm -C packages/core run play`
-  - Rolldown UI: `pnpm -C packages/rolldown run dev`
-  - Standalone core client: `pnpm -C packages/core run dev:standalone`
-- Tests: `pnpm test` (Vitest; projects under `packages/*` and `test`).
-- Typecheck: `pnpm typecheck` (via `vue-tsc -b`).
-- Lint: `pnpm lint`
-  - Use `pnpm lint --fix` to auto-resolve common issues.
-- Docs: `pnpm -C docs run docs` / `docs:build` / `docs:serve`.
+## Development
 
-## Conventions & Guardrails
-- Prefer workspace imports via aliases from `alias.ts`.
-- Keep RPC additions typed; use `defineRpcFunction` from kit when adding server functions.
-- Docks/views/terminals are registered through hosts on `DevToolsNodeContext`; mutations should update shared state (`@vitejs/devtools-kit/utils/shared-state`).
-- When touching websocket auth or storage, note persisted state lives in `node_modules/.vite/devtools/auth.json` (created by `createStorage`).
-- For Nuxt UI changes, base path must remain `/.devtools-vite/`; keep `clientAuth` considerations in mind if exposing over network.
-- Project is currently focused on Rolldown build-mode analysis; dev-mode support is deferred.
+```sh
+pnpm install                          # requires pnpm@10.x
+pnpm build                            # turbo run build
+pnpm test                             # Vitest
+pnpm typecheck                        # vue-tsc -b
+pnpm lint --fix                       # ESLint
+pnpm -C packages/core run play        # core playground
+pnpm -C packages/rolldown run dev     # rolldown UI dev
+pnpm -C packages/core run dev:standalone  # standalone client
+pnpm -C docs run docs                 # docs dev server
+```
+
+## Conventions
+
+- Use workspace aliases from `alias.ts`.
+- RPC functions must use `defineRpcFunction` from kit; always namespace IDs (`my-plugin:fn-name`).
+- Shared state via `@vitejs/devtools-kit/utils/shared-state`; keep values serializable.
+- Nuxt UI base paths: `/.devtools-rolldown/`, `/.devtools-vite/`, `/.devtools-self-inspect/`.
+- Shared UI components/preset in `packages/ui`; use `presetDevToolsUI` from `@vitejs/devtools-ui/unocss`.
+- Currently focused on Rolldown build-mode analysis; dev-mode support is deferred.
 
-## Useful Paths
-- Core runtime: `packages/core/src/node/*`
-- Core webcomponents: `packages/core/src/client/webcomponents`
-- Kit utilities: `packages/kit/src/utils/*`
-- RPC presets: `packages/rpc/src/presets/ws/*`
-- Rolldown UI app: `packages/rolldown/src/app`
-- Docs: `docs/guide/*`
+## Before PRs
+
+```sh
+pnpm lint && pnpm test && pnpm typecheck && pnpm build
+```
 
-## Quick Checks Before PRs
-- Run `pnpm lint && pnpm test && pnpm typecheck`.
-- Ensure `pnpm build` succeeds (regenerates Rolldown metadata if needed).
-- Follow conventional commit style (`feat:`, `fix:`, etc.). README flags project as WIP; set expectations accordingly.
+Follow conventional commits (`feat:`, `fix:`, etc.).
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
