#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobehub

# Idempotency guard
if grep -qF "4. **Register the desktop route tree in both configs:** `src/spa/router/desktopR" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,100 +1,124 @@
 # LobeHub Development Guidelines
 
-This document serves as a comprehensive guide for all team members when developing LobeHub.
-
-## Project Description
-
-You are developing an open-source, modern-design AI Agent Workspace: LobeHub (previously LobeChat).
+Guidelines for using AI coding agents in this LobeHub repository.
 
 ## Tech Stack
 
-- **Frontend**: Next.js 16, React 19, TypeScript
-- **UI Components**: Ant Design, @lobehub/ui, antd-style
-- **State Management**: Zustand, SWR
-- **Database**: PostgreSQL, PGLite, Drizzle ORM
-- **Testing**: Vitest, Testing Library
-- **Package Manager**: pnpm (monorepo structure)
+- Next.js 16 + React 19 + TypeScript
+- SPA inside Next.js with `react-router-dom`
+- `@lobehub/ui`, antd for components; antd-style for CSS-in-JS — **prefer `createStaticStyles` with `cssVar.*`** (zero-runtime); only fall back to `createStyles` + `token` when styles genuinely need runtime computation. See `.cursor/docs/createStaticStyles_migration_guide.md`.
+- react-i18next for i18n; zustand for state management
+- SWR for data fetching; TRPC for type-safe backend
+- Drizzle ORM with PostgreSQL; Vitest for testing
 
-## Directory Structure
+## Project Structure
 
 ```plaintext
 lobehub/
-├── apps/desktop/           # Electron desktop app
+├── apps/
+│   ├── desktop/            # Electron desktop app
+│   ├── cli/                # LobeHub CLI
+│   └── device-gateway/     # Device gateway service
 ├── packages/               # Shared packages (@lobechat/*)
 │   ├── database/           # Database schemas, models, repositories
 │   ├── agent-runtime/      # Agent runtime
 │   └── ...
 ├── src/
-│   ├── app/                # Next.js app router
-│   ├── spa/                # SPA entry points (entry.*.tsx) and router config
-│   ├── routes/             # SPA page components (roots)
-│   ├── features/           # Business components by domain
+│   ├── app/                # Next.js App Router (backend API + auth)
+│   │   ├── (backend)/     # API routes (trpc, webapi, etc.)
+│   │   ├── spa/            # SPA HTML template service
+│   │   └── [variants]/(auth)/  # Auth pages (SSR required)
+│   ├── routes/             # SPA page components (Vite)
+│   │   ├── (main)/         # Desktop pages
+│   │   ├── (mobile)/       # Mobile pages
+│   │   ├── (desktop)/      # Desktop-specific pages
+│   │   ├── (popup)/        # Popup window pages
+│   │   ├── onboarding/     # Onboarding pages
+│   │   └── share/          # Share pages
+│   ├── spa/                # SPA entry points and router config
+│   │   ├── entry.web.tsx   # Web entry
+│   │   ├── entry.mobile.tsx
+│   │   ├── entry.desktop.tsx
+│   │   ├── entry.popup.tsx
+│   │   └── router/         # React Router configuration
 │   ├── store/              # Zustand stores
 │   ├── services/           # Client services
 │   ├── server/             # Server services and routers
 │   └── ...
-├── .agents/skills/         # AI development skills
 └── e2e/                    # E2E tests (Cucumber + Playwright)
 ```
 
-## Development Workflow
+## SPA Routes and Features
 
-### Git Workflow
+SPA-related code is grouped under `src/spa/` (entries + router) and `src/routes/` (page segments). We use a **roots vs features** split: route trees only hold page segments; business logic and UI live in features.
 
-- **Branch strategy**: `canary` is the development branch (cloud production); `main` is the release branch (periodically cherry-picks from canary)
-- New branches should be created from `canary`; PRs should target `canary`
-- Use rebase for git pull
-- Git commit messages should prefix with gitmoji
-- Git branch name format: `feat/feature-name`
-- Use `.github/PULL_REQUEST_TEMPLATE.md` for PR descriptions
-- **Protection of local changes**: Never use `git restore`, `git checkout --`, `git reset --hard`, or any other command or workflow that can forcibly overwrite, discard, or silently replace user-owned uncommitted changes. Before any revert or restoration affecting existing files, inspect the working tree carefully and obtain explicit user confirmation.
+- **`src/spa/`** – SPA entry points (`entry.web.tsx`, `entry.mobile.tsx`, `entry.desktop.tsx`, `entry.popup.tsx`) and React Router config (`router/`, with `desktopRouter.config.*`, `mobileRouter.config.tsx`, `popupRouter.config.tsx`). Keeps router config next to entries to avoid confusion with `src/routes/`.
 
-### Package Management
+- **`src/routes/` (roots)**\
+  Only page-segment files: `_layout/index.tsx`, `index.tsx` (or `page.tsx`), and dynamic segments like `[id]/index.tsx`. Keep these **thin**: they should only import from `@/features/*` and compose layout/page, with no business logic or heavy UI.
+
+- **`src/features/`**\
+  Business components by **domain** (e.g. `Pages`, `PageEditor`, `Home`). Put layout chunks (sidebar, header, body), hooks, and domain-specific UI here. Each feature exposes an `index.ts` (or `index.tsx`) with clear exports.
 
-- Use `pnpm` as the primary package manager
-- Use `bun` to run npm scripts
-- Use `bunx` to run executable npm packages
+When adding or changing SPA routes:
 
-### Code Style Guidelines
+1. In `src/routes/`, add only the route segment files (layout + page) that delegate to features.
+2. Implement layout and page content under `src/features/<Domain>/` and export from there.
+3. In route files, use `import { X } from '@/features/<Domain>'` (or `import Y from '@/features/<Domain>/...'`). Do not add new `features/` folders inside `src/routes/`.
+4. **Register the desktop route tree in both configs:** `src/spa/router/desktopRouter.config.tsx` and `src/spa/router/desktopRouter.config.desktop.tsx` must stay in sync (same paths and nesting). Updating only one can cause **blank screens** if the other build path expects the route. `desktopRouter.sync.test.tsx` guards this invariant — keep it passing.
 
-#### TypeScript
+See the **spa-routes** skill (`.agents/skills/spa-routes/SKILL.md`) for the full convention and file-division rules.
 
-- Prefer interfaces over types for object shapes
+## Development
 
-### Testing Strategy
+### Starting the Dev Environment
 
 ```bash
-# Web tests
-bunx vitest run --silent='passed-only' '[file-path-pattern]'
+# SPA dev mode (frontend only, proxies API to localhost:3010)
+bun run dev:spa
 
-# Package tests (e.g., database)
-cd packages/[package-name] && bunx vitest run --silent='passed-only' '[file-path-pattern]'
+# Full-stack dev (Next.js + Vite SPA concurrently)
+bun run dev
 ```
 
-**Important Notes**:
+After `dev:spa` starts, the terminal prints a **Debug Proxy** URL:
 
-- Wrap file paths in single quotes to avoid shell expansion
-- Never run `bun run test` - this runs all tests and takes \~10 minutes
+```plaintext
+Debug Proxy: https://app.lobehub.com/_dangerous_local_dev_proxy?debug-host=http%3A%2F%2Flocalhost%3A9876
+```
 
-### Type Checking
+Open this URL to develop locally against the production backend (app.lobehub.com). The proxy page loads your local Vite dev server's SPA into the online environment, enabling HMR with real server config.
 
-- Use `bun run type-check` to check for type errors
+### Git Workflow
 
-### i18n
+- **Branch strategy**: `canary` is the development branch (cloud production); `main` is the release branch (periodically cherry-picks from canary)
+- New branches should be created from `canary`; PRs should target `canary`
+- Use rebase for `git pull`
+- Commit messages: prefix with gitmoji
+- Branch format: `<type>/<feature-name>`
 
-- **Keys**: Add to `src/locales/default/namespace.ts`
-- **Dev**: Translate `locales/zh-CN/namespace.json` locale file only for preview
-- DON'T run `pnpm i18n`, let CI auto handle it
+### Package Management
 
-## SPA Routes and Features
+- `pnpm` for dependency management
+- `bun` to run npm scripts
+- `bunx` for executable npm packages
 
-- **`src/routes/`** holds only page segments (`_layout/index.tsx`, `index.tsx`, `[id]/index.tsx`). Keep route files **thin** — import from `@/features/*` and compose, no business logic.
-- **`src/features/`** holds business components by **domain** (e.g. `Pages`, `PageEditor`, `Home`). Layout pieces, hooks, and domain UI go here.
-- **Desktop router parity:** When changing the main SPA route tree, update **both** `src/spa/router/desktopRouter.config.tsx` (dynamic imports) and `src/spa/router/desktopRouter.config.desktop.tsx` (sync imports) so paths and nesting match. Changing only one can leave routes unregistered and cause **blank screens**.
-- See the **spa-routes** skill (`.agents/skills/spa-routes/SKILL.md`) for the full convention and file-division rules.
+### Testing
 
-## Skills (Auto-loaded)
+```bash
+# Run specific test (NEVER run `bun run test` - takes ~10 minutes)
+bunx vitest run --silent='passed-only' '[file-path]'
+
+# Database package
+cd packages/database && bunx vitest run --silent='passed-only' '[file]'
+```
 
-All AI development skills are available in `.agents/skills/` directory and auto-loaded by Claude Code when relevant.
+- Prefer `vi.spyOn` over `vi.mock`
+- Tests must pass type check: `bun run type-check`
+- After 2 failed fix attempts, stop and ask for help
+
+### i18n
 
-**IMPORTANT**: When reviewing PRs or code diffs, ALWAYS read `.agents/skills/code-review/SKILL.md` first.
+- Add keys to a namespace file under `src/locales/default/` (e.g. `agent.ts`, `auth.ts`)
+- For dev preview: translate `locales/zh-CN/` and `locales/en-US/`
+- Don't run `pnpm i18n` - CI handles it
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,123 +1 @@
-# CLAUDE.md
-
-Guidelines for using Claude Code in this LobeHub repository.
-
-## Tech Stack
-
-- Next.js 16 + React 19 + TypeScript
-- SPA inside Next.js with `react-router-dom`
-- `@lobehub/ui`, antd for components; antd-style for CSS-in-JS — **prefer `createStaticStyles` with `cssVar.*`** (zero-runtime); only fall back to `createStyles` + `token` when styles genuinely need runtime computation. See `.cursor/docs/createStaticStyles_migration_guide.md`.
-- react-i18next for i18n; zustand for state management
-- SWR for data fetching; TRPC for type-safe backend
-- Drizzle ORM with PostgreSQL; Vitest for testing
-
-## Project Structure
-
-```plaintext
-lobehub/
-├── apps/desktop/           # Electron desktop app
-├── packages/               # Shared packages (@lobechat/*)
-│   ├── database/           # Database schemas, models, repositories
-│   ├── agent-runtime/      # Agent runtime
-│   └── ...
-├── src/
-│   ├── app/                # Next.js App Router (backend API + auth)
-│   │   ├── (backend)/     # API routes (trpc, webapi, etc.)
-│   │   ├── spa/            # SPA HTML template service
-│   │   └── [variants]/(auth)/  # Auth pages (SSR required)
-│   ├── routes/             # SPA page components (Vite)
-│   │   ├── (main)/         # Desktop pages
-│   │   ├── (mobile)/       # Mobile pages
-│   │   ├── (desktop)/      # Desktop-specific pages
-│   │   ├── onboarding/     # Onboarding pages
-│   │   └── share/          # Share pages
-│   ├── spa/                # SPA entry points and router config
-│   │   ├── entry.web.tsx   # Web entry
-│   │   ├── entry.mobile.tsx
-│   │   ├── entry.desktop.tsx
-│   │   └── router/         # React Router configuration
-│   ├── store/              # Zustand stores
-│   ├── services/           # Client services
-│   ├── server/             # Server services and routers
-│   └── ...
-└── e2e/                    # E2E tests (Cucumber + Playwright)
-```
-
-## SPA Routes and Features
-
-SPA-related code is grouped under `src/spa/` (entries + router) and `src/routes/` (page segments). We use a **roots vs features** split: route trees only hold page segments; business logic and UI live in features.
-
-- **`src/spa/`** – SPA entry points (`entry.web.tsx`, `entry.mobile.tsx`, `entry.desktop.tsx`) and React Router config (`router/`). Keeps router config next to entries to avoid confusion with `src/routes/`.
-
-- **`src/routes/` (roots)**\
-  Only page-segment files: `_layout/index.tsx`, `index.tsx` (or `page.tsx`), and dynamic segments like `[id]/index.tsx`. Keep these **thin**: they should only import from `@/features/*` and compose layout/page, with no business logic or heavy UI.
-
-- **`src/features/`**\
-  Business components by **domain** (e.g. `Pages`, `PageEditor`, `Home`). Put layout chunks (sidebar, header, body), hooks, and domain-specific UI here. Each feature exposes an `index.ts` (or `index.tsx`) with clear exports.
-
-When adding or changing SPA routes:
-
-1. In `src/routes/`, add only the route segment files (layout + page) that delegate to features.
-2. Implement layout and page content under `src/features/<Domain>/` and export from there.
-3. In route files, use `import { X } from '@/features/<Domain>'` (or `import Y from '@/features/<Domain>/...'`). Do not add new `features/` folders inside `src/routes/`.
-4. **Register the desktop route tree in both configs:** `src/spa/router/desktopRouter.config.tsx` and `src/spa/router/desktopRouter.config.desktop.tsx` must stay in sync (same paths and nesting). Updating only one can cause **blank screens** if the other build path expects the route.
-
-See the **spa-routes** skill (`.agents/skills/spa-routes/SKILL.md`) for the full convention and file-division rules.
-
-## Development
-
-### Starting the Dev Environment
-
-```bash
-# SPA dev mode (frontend only, proxies API to localhost:3010)
-bun run dev:spa
-
-# Full-stack dev (Next.js + Vite SPA concurrently)
-bun run dev
-```
-
-After `dev:spa` starts, the terminal prints a **Debug Proxy** URL:
-
-```plaintext
-Debug Proxy: https://app.lobehub.com/_dangerous_local_dev_proxy?debug-host=http%3A%2F%2Flocalhost%3A9876
-```
-
-Open this URL to develop locally against the production backend (app.lobehub.com). The proxy page loads your local Vite dev server's SPA into the online environment, enabling HMR with real server config.
-
-### Git Workflow
-
-- **Branch strategy**: `canary` is the development branch (cloud production); `main` is the release branch (periodically cherry-picks from canary)
-- New branches should be created from `canary`; PRs should target `canary`
-- Use rebase for `git pull`
-- Commit messages: prefix with gitmoji
-- Branch format: `<type>/<feature-name>`
-
-### Package Management
-
-- `pnpm` for dependency management
-- `bun` to run npm scripts
-- `bunx` for executable npm packages
-
-### Testing
-
-```bash
-# Run specific test (NEVER run `bun run test` - takes ~10 minutes)
-bunx vitest run --silent='passed-only' '[file-path]'
-
-# Database package
-cd packages/database && bunx vitest run --silent='passed-only' '[file]'
-```
-
-- Prefer `vi.spyOn` over `vi.mock`
-- Tests must pass type check: `bun run type-check`
-- After 2 failed fix attempts, stop and ask for help
-
-### i18n
-
-- Add keys to `src/locales/default/namespace.ts`
-- For dev preview: translate `locales/zh-CN/` and `locales/en-US/`
-- Don't run `pnpm i18n` - CI handles it
-
-## Skills (Auto-loaded by Claude)
-
-Claude Code automatically loads relevant skills from `.agents/skills/`.
+@AGENTS.md
PATCH

echo "Gold patch applied."
