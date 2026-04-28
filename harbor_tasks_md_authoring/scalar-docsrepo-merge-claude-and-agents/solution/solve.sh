#!/usr/bin/env bash
set -euo pipefail

cd /workspace/scalar

# Idempotency guard
if grep -qF "When a **Linear ticket** ID (e.g. `DOC-5102`, `ENG-123`) or a **GitHub issue** n" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,10 +1,14 @@
-# AGENTS.md – AI Agent Guide for Scalar
+# AGENTS.md - AI Agent Guide for Scalar
 
-This file helps AI coding agents (Cursor, GitHub Copilot, etc.) work effectively in the Scalar codebase. For full development guidelines, see [CLAUDE.md](./CLAUDE.md).
+This file helps AI coding agents (Cursor, Claude Code, GitHub Copilot, etc.) work effectively in the Scalar codebase. It is the canonical agent guide for this repository.
 
 ## Project Overview
 
-Scalar is a Vue 3 + TypeScript monorepo for API documentation and testing. It uses pnpm workspaces, Turbo for builds, and includes many packages and framework integrations.
+Scalar is a Vue 3 + TypeScript monorepo for API documentation and testing.
+
+- It produces `@scalar/api-reference` (renders OpenAPI docs) and `@scalar/api-client` (API testing client)
+- It includes 40+ supporting packages and 18 framework integrations (Express, Fastify, Hono, NestJS, Next.js, Nuxt, etc.)
+- It uses pnpm workspaces, Turbo for build orchestration, Vite for Vue packages, and esbuild for pure TypeScript packages
 
 - **Frontend**: Vue 3, Composition API, TypeScript
 - **Styling**: Tailwind CSS
@@ -23,6 +27,14 @@ pnpm install
 pnpm build:packages
 ```
 
+## Commands
+
+```bash
+pnpm install                    # Install dependencies
+pnpm build:packages             # Build all packages (required before first dev)
+pnpm clean:build                # Clean everything, reinstall, rebuild
+```
+
 ## Key Commands
 
 | Task | Command |
@@ -31,7 +43,9 @@ pnpm build:packages
 | Build integrations | `pnpm build:integrations` |
 | Clean build | `pnpm clean:build` |
 | Run unit tests | `pnpm test` |
-| Run tests (single package) | `pnpm vitest packages/api-client --run` |
+| Run tests (single package, single run) | `pnpm vitest packages/helpers --run` |
+| Run tests (single package, watch mode) | `pnpm vitest packages/api-client` |
+| Run tests filtered by name | `pnpm test your-test-name` |
 | Lint check | `pnpm lint:check` |
 | Lint fix | `pnpm lint:fix` |
 | Format | `pnpm format` |
@@ -43,8 +57,8 @@ There is no single root `pnpm dev`. Run per package:
 
 ```bash
 pnpm --filter @scalar/api-client dev
-pnpm --filter api-reference dev
-pnpm --filter components dev
+pnpm --filter @scalar/api-reference dev
+pnpm --filter @scalar/components dev
 ```
 
 | Package | Purpose |
@@ -63,41 +77,136 @@ pnpm script run test-servers
 pnpm script wait -p 5051 5052
 ```
 
+## Architecture
+
+### Workspace Layout
+
+- `packages/` - Core libraries (45 packages). Each is an npm package under `@scalar/`.
+- `integrations/` - Framework-specific wrappers (Express, Fastify, Next.js, Nuxt, etc.)
+- `projects/` - Deployable apps (`scalar-app`, `proxy-scalar-com`, `client-scalar-com`)
+- `examples/` - Usage examples for various frameworks
+- `tooling/` - Internal build scripts and changelog generator
+
 ## Directory Structure
 
+```text
+packages/      # Core packages (@scalar/*)
+integrations/  # Framework integrations (Express, FastAPI, etc.)
+examples/      # Example apps
+projects/      # Supporting projects (e.g. proxy-scalar-com)
+tooling/       # Internal scripts and build helpers
 ```
-packages/           # Core packages (@scalar/*)
-integrations/       # Framework integrations (Express, FastAPI, etc.)
-examples/           # Example apps
-projects/           # Supporting projects (e.g. proxy-scalar-com)
-```
 
-## Code Conventions
+### Build System
+
+Two build strategies use standard tools directly (no custom build CLI):
+
+1. **`tsc` + `tsc-alias`**
+   - For pure TypeScript packages (helpers, types, openapi-parser, integrations)
+   - Uses `tsconfig.build.json` per package
+2. **`vite build`**
+   - For Vue component packages (`components`, `api-reference`, `api-client`)
+   - Uses Vite 8 + Rolldown, extracts CSS, preserves modules
+   - Shared build helpers live in `tooling/scripts/vite-lib-config.ts`
+
+Both strategies externalize dependencies (nothing is bundled into library output). `api-reference` is special because it has both a default build and a standalone build (`vite.standalone.config.ts`) that bundles everything for CDN usage.
+
+Type checking uses `tsc --noEmit` (pure TS) or `vue-tsc --noEmit` (Vue packages).
+
+### Key Package Relationships
+
+- `@scalar/core` - Shared rendering logic consumed by `api-reference` and integrations
+- `@scalar/themes` - CSS variables and design tokens used across UI packages
+- `@scalar/components` - Vue component library (with Storybook)
+- `@scalar/oas-utils` - OpenAPI utilities shared across `api-reference` and `api-client`
+- `@scalar/types` - Shared TypeScript types; import from specific entry points (`@scalar/types/api-reference`, etc.), not the root
+
+### Dependency Versioning
+
+All workspace packages use `workspace:*` for internal dependencies. Shared third-party versions are defined in `pnpm-workspace.yaml` under `catalogs:` and referenced as `catalog:*` in `package.json` files.
+
+### Tooling Split
+
+- **Biome**: Linting and formatting for `.ts` files
+- **ESLint**: Linting for `.vue` files
+- **Prettier**: Formatting for `.vue`, `.md`, `.json`, `.css`, `.html`, `.yml` files
+- **Lefthook**: Pre-commit hooks running Prettier + Biome on staged files
+
+## Code Standards
+
+### TypeScript
+
+- Prefer `type` over `interface`
+- Use explicit return types for functions
+- Avoid `any`; use `unknown` when the type is unclear
+- Avoid enums; use string literal unions
+- Use `const` instead of `let` whenever possible
+- Use `type` keyword for type-only imports (`import type { Foo }`)
+- Prefer arrow functions over function declarations
+- Use single quotes, trailing commas, and semicolons only as needed
 
-- **Vue**: Composition API, `<script setup>`, TypeScript
-- **Types**: Prefer `type` over `interface`
-- **Files**: kebab-case (e.g. `api-client.ts`)
-- **Components**: PascalCase (e.g. `ApiClient.vue`)
-- **Tests**: `*.test.ts` alongside source, `describe('filename')`
+### Vue Components
+
+- Use Composition API with `<script setup lang="ts">`
+- Use Tailwind CSS utility classes for styling
+- Destructure props: `const { prop1, prop2 = 'default' } = defineProps<Props>()`
+- Explicitly type `defineProps` and `defineEmits`
+- Keep templates clean; use computed properties over inline logic
+- Recommended `<script setup>` order: imports, props/emits, state/computed/methods, lifecycle hooks
+
+### Comments and Docs
+
+- Explain **why**, not what
+- Use a friendly, human tone
+- Avoid contractions (use "do not" instead of "don't")
+- Add JSDoc for exported types and functions
+- Leave TODO comments for temporary solutions
 
 ## Testing
 
 - **Unit tests**: Vitest, `*.test.ts` next to source
 - **E2E**: Playwright in `packages/api-reference` and `packages/components`
 - **Integration tests**: `pnpm vitest integrations/*`
 
+### Testing Standards
+
+- Always import `describe`, `it`, and `expect` explicitly from `vitest` (no globals)
+- Place test files as `name.test.ts` alongside source
+- Keep top-level `describe()` matching the file name
+- Do not start test descriptions with "should" (`it('generates a slug')`, not `it('should generate a slug')`)
+- Minimize mocking; prefer pure functions
+- For Vue component tests, verify behavior, not DOM structure or Tailwind class details
+
+### Biome Lint Rules to Know
+
+- `noBarrelFile: error` - No barrel files (except `index.ts` entry points)
+- `noReExportAll: warn` - Avoid `export * from` (error in `api-reference` and `openapi-parser`)
+- `noTsIgnore: error` - No `@ts-ignore` (use `@ts-expect-error` with explanation if needed)
+- `useAwait: error` - Async functions must use `await`
+- `noExportsInTest: error` - Do not export from test files
+- `noFloatingPromises: warn` - Handle all promises
+
 ## Git Workflow
 
-- **Branch naming**: `claude/feature-description`, `claude/fix-description`
-- **Commits**: Conventional commits, present tense, scope when relevant
+### Branch Naming
+
+- `claude/feature-description` - New features
+- `claude/fix-description` - Bug fixes
+- `claude/chore-description` - Maintenance
+
+### Commit Messages
+
+- Use conventional commits, for example: `feat(api-client): add new endpoint`
+- Use present tense ("add" instead of "added")
+- Prefer scope when relevant
 
 ## PR Requirements
 
 ### Semantic PR titles
 
 PR titles must follow `type(scope): subject`:
 
-```
+```text
 fix(api-client): crashes when API returns null
 ^   ^            ^
 |   |            subject
@@ -107,36 +216,37 @@ type (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
 
 ### Ticket and issue linking
 
-When a **Linear ticket** ID (e.g. `DOC-5102`, `ENG-123`) or a **GitHub issue** number/URL is provided in the prompt, instructions, or a related Slack thread, you **must** link it in the PR so that project-management integrations can track progress automatically.
+When a **Linear ticket** ID (e.g. `DOC-5102`, `ENG-123`) or a **GitHub issue** number/URL is provided in the prompt, instructions, or related Slack thread, link it in the PR so project-management integrations can track progress automatically.
 
-If a GitHub issue number is available, include it explicitly in the PR description using `See #123` (non-closing) or `Fixes #123` (auto-closing on merge).
+If a GitHub issue number is available, include it in the PR description using `See #123` (non-closing) or `Fixes #123` (auto-closing on merge).
 
 #### Linear tickets
 
-Include the Linear issue ID in the **PR branch name** or **PR description** using a magic word. Linear's GitHub integration detects these and links the PR to the issue. Do **not** put the issue ID in the PR title — titles must follow the conventional commit format (e.g. `feat(api-reference): add my new feature`).
+Include the Linear issue ID in the branch name or PR description using a magic word. Do **not** put the issue ID in the PR title.
 
-**Closing magic words** (move the issue to Done when the PR merges):
+**Closing magic words**:
 `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`
 
-**Non-closing magic words** (link without auto-closing):
+**Non-closing magic words**:
 `ref`, `refs`, `references`, `part of`, `related to`, `contributes to`, `toward`, `towards`
 
-Examples (in the PR description):
+Examples:
 
-```
+```text
 Fixes DOC-5102
 Part of ENG-123
 Resolves DOC-5102, ENG-456
 ```
 
-You can also use the full Linear URL: `Fixes https://linear.app/scalar/issue/DOC-5102/title`.
+You can also use full Linear URLs, for example:
+`Fixes https://linear.app/scalar/issue/DOC-5102/title`.
 
-To link multiple issues, list them after the magic word separated by commas: `Fixes ENG-123, DES-5, ENG-256`.
+To link multiple issues:
+`Fixes ENG-123, DES-5, ENG-256`.
 
 #### GitHub issues
 
-Use GitHub's closing keywords in the PR description to link and auto-close GitHub issues when the PR merges:
-
+Use GitHub closing keywords in the PR description to link and auto-close issues on merge:
 `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`
 
 | Scenario | Syntax | Example |
@@ -158,23 +268,27 @@ Closes #42
 
 If both a Linear ticket and a GitHub issue are provided, include both.
 
-> **Tip:** Magic words must appear in the PR description (not in PR comments) for Linear to detect them. For GitHub issues, keywords work in both the PR description and commit messages.
+> Tip: Magic words must appear in the PR description (not PR comments) for Linear detection. For GitHub issues, keywords work in both PR descriptions and commit messages.
 
 ### Changesets
 
-For code changes in `packages/*` and `integrations/*`, a changeset is required. Use `patch` or `minor` version bumps based on impact; do not use `major`.
+For code changes in `packages/*` and `integrations/*`, include a changeset using `patch` or `minor` (do not use `major`).
+
+Before opening or updating a PR, run:
 
-Before opening or updating a PR, run `pnpm changeset status` to verify changesets and catch missing or invalid changeset entries.
+```bash
+pnpm changeset status
+```
 
-If your PR will cause a version bump for any package, add a changeset:
+If a package version should bump, add a changeset:
 
 ```bash
 pnpm changeset
 ```
 
 ### Pre-PR command checklist
 
-After making code changes, run `pnpm format` and `pnpm knip` before opening or updating a PR.
+After making code changes, run:
 
 ```bash
 pnpm format
@@ -183,35 +297,35 @@ pnpm knip
 
 ## Visual Testing
 
-When making changes that affect the UI, **PRs must include visual artifacts** (screenshots and/or demo videos) demonstrating the visual impact. Most package dependencies trickle up into three main visual surfaces: `api-reference`, `api-client`, and `components`. Test your changes in whichever playground is relevant.
+When making UI changes, PRs must include visual artifacts (screenshots and/or demo videos) demonstrating impact. Most package dependencies trickle up into three main visual surfaces: `api-reference`, `api-client`, and `components`.
 
 ### Prerequisites
 
-Build all packages before running any playground (dependencies must be compiled first):
+Build all packages before running any playground:
 
 ```bash
 pnpm install
 pnpm build:packages
 ```
 
-Alternatively, `pnpm turbo dev` or `pnpm turbo build` in a package directory will automatically build upstream dependencies via Turbo.
+Alternatively, `pnpm turbo dev` or `pnpm turbo build` in a package directory can auto-build upstream dependencies.
 
 ### Playgrounds
 
-Each playground can be started with `pnpm dev` inside its package directory, or from the repo root using Turbo (which auto-builds dependencies):
+Each playground can be started with `pnpm dev` inside its package directory, or from repo root with Turbo:
 
 | Package | Quick start | Turbo | Details |
-|---------|------------|-------|---------|
+|---------|-------------|-------|---------|
 | `api-reference` | `cd packages/api-reference && pnpm dev` | `pnpm turbo --filter @scalar/api-reference dev` | [`AGENTS.md`](./packages/api-reference/AGENTS.md) |
 | `api-client` | `cd packages/api-client && pnpm dev` | `pnpm turbo --filter @scalar/api-client dev` | [`AGENTS.md`](./packages/api-client/AGENTS.md) |
 | `components` | `cd packages/components && pnpm dev` | `pnpm turbo --filter @scalar/components dev` | [`AGENTS.md`](./packages/components/AGENTS.md) |
 
-The `api-client` has multiple layouts (web, app, modal) — see its package `AGENTS.md` for details.
+The `api-client` has multiple layouts (web, app, modal) - see its package `AGENTS.md` for details.
 
 ### Which playground to use
 
 | Change area | Primary playground | Secondary |
-|-------------|-------------------|-----------|
+|-------------|--------------------|-----------|
 | Base components (buttons, inputs, modals) | `components` Storybook | `api-reference`, `api-client` |
 | Themes, CSS variables, design tokens | `api-reference` | `api-client`, `components` |
 | Sidebar, search, OpenAPI rendering | `api-reference` | `api-client` |
@@ -221,35 +335,33 @@ The `api-client` has multiple layouts (web, app, modal) — see its package `AGE
 
 ### Artifact guidelines for PRs
 
-When making UI changes, **PRs must include visual artifacts** (screenshots and videos) embedded directly in the PR description. Cursor Cloud Agents can post these artifacts to GitHub automatically.
+When making UI changes, embed artifacts directly in the PR description. Cursor Cloud Agents can upload these when referenced as absolute paths.
 
 #### How it works
 
-1. **Save artifacts** to `/opt/cursor/artifacts/` with descriptive snake_case names (e.g. `screenshot_sidebar_before.png`, `demo_dark_mode_toggle.mp4`).
-2. **Reference artifacts in the PR description** using HTML tags with absolute file paths. The platform automatically uploads them and rewrites the paths to public URLs.
+1. Save artifacts to `/opt/cursor/artifacts/` using descriptive snake_case names.
+2. Reference artifacts in PR descriptions with absolute HTML paths.
+3. Use the `ManagePullRequest` tool to create/update PR descriptions.
+
+Example:
 
 ```html
-<!-- Screenshots -->
 <img src="/opt/cursor/artifacts/screenshot_before.png" alt="Before change" />
 <img src="/opt/cursor/artifacts/screenshot_after.png" alt="After change" />
-
-<!-- Videos -->
 <video src="/opt/cursor/artifacts/demo_feature.mp4" controls></video>
 ```
 
-3. **Use the `ManagePullRequest` tool** to create or update the PR with these references in the body.
-
 #### What to capture
 
-- Include **before and after** screenshots when modifying existing UI.
-- For new features, include screenshots showing the feature in context.
-- Use the playground that best demonstrates the change.
-- If the change affects multiple playgrounds, include screenshots from each.
-- For interactive changes (animations, state transitions, flows), record a **demo video** showing the feature working end-to-end.
+- Before and after screenshots for modified UI
+- In-context screenshots for new features
+- Artifacts from the most relevant playground
+- Artifacts from multiple playgrounds if the change spans surfaces
+- Demo videos for interactive behavior
 
 #### PR description format
 
-Add a `## Visual` section to the PR description with the artifacts:
+Add a `## Visual` section:
 
 ```markdown
 ## Visual
@@ -259,8 +371,18 @@ Add a `## Visual` section to the PR description with the artifacts:
 <video src="/opt/cursor/artifacts/demo_feature.mp4" controls></video>
 ```
 
+## OpenAPI Terminology
+
+Use consistent terminology:
+
+- **OpenAPI** (not "Swagger") - specification format
+- **API description** (not "API spec" or "API definition") - metadata document
+- **Schema** - data model for request/response shapes
+- **Dereference** - replace all `$ref` with their values
+- **Bundle** - pull external `$ref` values into a single file
+- **Resolve** - look up value at a `$ref` without modifying the document
+
 ## Further Reading
 
-- [CONTRIBUTING.md](./CONTRIBUTING.md) – PR requirements, changesets, auto-generated files
-- [CLAUDE.md](./CLAUDE.md) – Full development guide, Vue/TS conventions, testing
-- [.cursor/rules/cloud-agents-starter-skill.mdc](./.cursor/rules/cloud-agents-starter-skill.mdc) – Runbook for CI parity and test servers
+- [CONTRIBUTING.md](./CONTRIBUTING.md) - PR requirements, changesets, auto-generated files
+- [.cursor/rules/cloud-agents-starter-skill.mdc](./.cursor/rules/cloud-agents-starter-skill.mdc) - Runbook for CI parity and test servers
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,148 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-
-Scalar is a Vue 3 + TypeScript monorepo for API documentation and testing. It produces `@scalar/api-reference` (renders OpenAPI docs) and `@scalar/api-client` (API testing client), plus 40+ supporting packages and 18 framework integrations (Express, Fastify, Hono, NestJS, Next.js, Nuxt, etc.).
-
-Uses pnpm workspaces, Turbo for build orchestration, Vite for Vue packages, esbuild for pure TS packages.
-
-## Commands
-
-```bash
-pnpm install                    # Install dependencies
-pnpm build:packages             # Build all packages (required before first dev)
-pnpm clean:build                # Clean everything, reinstall, rebuild
-
-# Development (per-package, not root-level)
-pnpm --filter @scalar/api-reference dev
-pnpm --filter @scalar/components dev    # Storybook on port 5100
-pnpm --filter @scalar/api-client dev
-
-# Testing
-pnpm test                               # All tests (watch mode)
-pnpm vitest packages/helpers --run       # Single package, single run
-pnpm vitest packages/api-client          # Single package, watch mode
-pnpm test your-test-name                 # Filter by test name
-
-# Some tests need test servers running first
-pnpm script run test-servers             # Start void-server (5052) + proxy (5051)
-pnpm script wait -p 5051 5052            # Wait for ports
-
-# E2E (Playwright, per-package)
-cd packages/api-reference && pnpm test:e2e
-cd packages/components && pnpm test:e2e
-
-# Code quality
-pnpm format                     # Prettier (vue/md/json) + Biome (ts)
-pnpm lint:check                 # Biome lint
-pnpm lint:fix                   # Biome + ESLint auto-fix
-pnpm types:check                # TypeScript checking via Turbo
-```
-
-## Architecture
-
-### Workspace Layout
-
-- `packages/` — Core libraries (45 packages). Each is an npm package under `@scalar/`.
-- `integrations/` — Framework-specific wrappers (Express, Fastify, Next.js, Nuxt, etc.)
-- `projects/` — Deployable apps (`scalar-app`, `proxy-scalar-com`, `client-scalar-com`)
-- `examples/` — Usage examples for various frameworks
-- `tooling/` — Internal build scripts and changelog generator
-
-### Build System
-
-Two build strategies using standard tools directly (no custom build CLI):
-
-1. **`tsc` + `tsc-alias`** — For pure TypeScript packages (helpers, types, openapi-parser, integrations). Uses `tsconfig.build.json` per package.
-
-2. **`vite build`** — For Vue component packages (components, api-reference, api-client). Uses Vite 8 + Rolldown, extracts CSS, preserves modules. Shared build helpers in `tooling/scripts/vite-lib-config.ts`.
-
-Both externalize all dependencies (nothing is bundled into library output). `api-reference` is special: it has both a default build and a standalone build (`vite.standalone.config.ts`) that bundles everything for CDN usage.
-
-Type checking uses `tsc --noEmit` (pure TS) or `vue-tsc --noEmit` (Vue packages).
-
-### Key Package Relationships
-
-- `@scalar/core` — Shared rendering logic consumed by api-reference and integrations
-- `@scalar/themes` — CSS variables and design tokens used across all UI packages
-- `@scalar/components` — Vue component library (with Storybook)
-- `@scalar/oas-utils` — OpenAPI spec utilities shared across api-reference and api-client
-- `@scalar/types` — Shared TypeScript types. Import from specific entry points (`@scalar/types/api-reference`, etc.), not the root.
-
-### Dependency Versioning
-
-All workspace packages use `workspace:*` for internal deps. Shared third-party versions are defined in `pnpm-workspace.yaml` under `catalogs:` and referenced as `catalog:*` in package.json files.
-
-### Tooling Split
-
-- **Biome**: Linting and formatting for `.ts` files
-- **ESLint**: Linting for `.vue` files
-- **Prettier**: Formatting for `.vue`, `.md`, `.json`, `.css`, `.html`, `.yml` files
-- **Lefthook**: Pre-commit hooks running Prettier + Biome on staged files
-
-## Code Standards
-
-### TypeScript
-- Prefer `type` over `interface`
-- Explicit return types for functions
-- Avoid `any`; use `unknown` when the type is unclear
-- Avoid enums; use string literal unions
-- Always use `const` instead of `let`
-- Use `type` keyword for type-only imports (`import type { Foo }`)
-- Arrow functions preferred over function declarations
-- Single quotes, trailing commas, semicolons only as needed
-
-### Vue Components
-- Composition API with `<script setup lang="ts">`
-- Use Tailwind CSS utility classes for styling
-- Destructure props: `const { prop1, prop2 = 'default' } = defineProps<Props>()`
-- Explicitly type `defineProps` and `defineEmits`
-- Keep templates clean: use computed properties over inline logic
-- `<script setup>` order: imports, props/emits, state/computed/methods, lifecycle hooks
-
-### Comments
-- Explain **why**, not what
-- Friendly, human tone
-- Avoid contractions (use "do not" instead of "don't")
-- JSDoc for exported types and functions
-- Leave TODO comments for temporary solutions
-
-### Testing
-- Vitest for unit tests, Playwright for E2E
-- Always import `describe`, `it`, `expect` explicitly from `vitest` (no globals)
-- Test files: `name.test.ts` alongside the source file
-- Top-level `describe()` matches the file name
-- Do not start test descriptions with "should": `it('generates a slug')` not `it('should generate a slug')`
-- Minimize mocking; prefer pure functions
-- Vue component tests: test behavior, not DOM structure or Tailwind classes
-
-### Biome Lint Rules to Know
-- `noBarrelFile: error` — No barrel files (except `index.ts` entry points)
-- `noReExportAll: warn` — Avoid `export * from` (error in api-reference and openapi-parser)
-- `noTsIgnore: error` — No `@ts-ignore` (use `@ts-expect-error` with explanation if needed)
-- `useAwait: error` — Async functions must use `await`
-- `noExportsInTest: error` — Do not export from test files
-- `noFloatingPromises: warn` — Handle all promises
-
-## Git Workflow
-
-### Branch Naming
-- `claude/feature-description` — New features
-- `claude/fix-description` — Bug fixes
-- `claude/chore-description` — Maintenance
-
-### Commit Messages
-- Conventional commits: `feat(api-client): add new endpoint`
-- Present tense ("add" not "added")
-
-## OpenAPI Terminology
-
-Use correct terminology when working with OpenAPI-related code:
-- **OpenAPI** (not "Swagger") — The specification format
-- **API description** (not "API spec" or "API definition") — The metadata document
-- **Schema** — Data model describing request/response shapes
-- **Dereference** — Replace all `$ref` with their values
-- **Bundle** — Pull external `$ref`s into a single file
-- **Resolve** — Look up the value at a `$ref` without modifying the document
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
