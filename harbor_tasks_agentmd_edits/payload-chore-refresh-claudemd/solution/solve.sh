#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied (CLAUDE.md is a regular file with content)
if [[ -f "CLAUDE.md" ]] && [[ ! -L "CLAUDE.md" ]] && grep -q "Project Structure" CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/.gitignore b/.gitignore
index f120ec19357..18a1bf6cc56 100644
--- a/.gitignore
+++ b/.gitignore
@@ -9,6 +9,8 @@ dist
 # Local AI Agent files
 AGENTS.local.md
 CLAUDE.local.md
+.claude/commands/*.local.md
+.claude/artifacts

 # Custom actions
 !.github/actions/**/dist
diff --git a/AGENTS.md b/AGENTS.md
deleted file mode 100644
index bd532559101..00000000000
--- a/AGENTS.md
+++ /dev/null
@@ -1,54 +0,0 @@
-# Payload Monorepo Agent Instructions
-
-## Project Structure
-
-- Packages are located in the `packages/` directory.
-  - The main Payload package is `packages/payload`. This contains the core functionality.
-  - Database adapters are in `packages/db-*`.
-  - The UI package is in `packages/ui`.
-  - The Next.js integration is in `packages/next`.
-  - Rich text editor packages are in `packages/richtext-*`.
-  - Storage adapters are in `packages/storage-*`.
-  - Email adapters are in `packages/email-*`.
-  - Plugins which add additional functionality are in `packages/plugin-*`.
-- Documentation is in the `docs/` directory.
-- Monorepo tooling is in the `tools/` directory.
-- Test suites and configs are in the `test/` directory.
-- LLMS.txt is at URL: https://payloadcms.com/llms.txt
-- LLMS-FULL.txt is at URL: https://payloadcms.com/llms-full.txt
-
-## Dev environment tips
-
-- Any package can be built using a `pnpm build:*` script defined in the root `package.json`. These typically follow the format `pnpm build:<directory_name>`. The options are all of the top-level directories inside the `packages/` directory. Ex `pnpm build:db-mongodb` which builds the `packages/db-mongodb` package.
-- ALL packages can be built with `pnpm build:all`.
-- Use `pnpm dev` to start the monorepo dev server. This loads the default config located at `test/_community/config.ts`.
-- Specific dev configs for each package can be run with `pnpm dev <directory_name>`. The options are all of the top-level directories inside the `test/` directory. Ex `pnpm dev fields` which loads the `test/fields/config.ts` config. The directory name can either encompass a single area of functionality or be the name of a specific package.
-
-## Testing instructions
-
-- There are unit, integration, and e2e tests in the monorepo.
-- Unit tests can be run with `pnpm test:unit`.
-- Integration tests can be run with `pnpm test:int`. Individual test suites can be run with `pnpm test:int <directory_name>`, which will point at `test/<directory_name>/int.spec.ts`.
-- E2E tests can be run with `pnpm test:e2e`.
-- All tests can be run with `pnpm test`.
-- Prefer running `pnpm test:int` for verifying local code changes.
-
-## PR Guidelines
-
-- This repository follows conventional commits for PR titles
-- PR Title format: <type>(<scope>): <title>. Title must start with a lowercase letter.
-- Valid types are build, chore, ci, docs, examples, feat, fix, perf, refactor, revert, style, templates, test
-- Prefer `feat` for new features and `fix` for bug fixes.
-- Valid scopes are the following regex patterns: cpa, db-\*, db-mongodb, db-postgres, db-vercel-postgres, db-sqlite, drizzle, email-\*, email-nodemailer, email-resend, eslint, graphql, live-preview, live-preview-react, next, payload-cloud, plugin-cloud, plugin-cloud-storage, plugin-form-builder, plugin-import-export, plugin-multi-tenant, plugin-nested-docs, plugin-redirects, plugin-search, plugin-sentry, plugin-seo, plugin-stripe, richtext-\*, richtext-lexical, richtext-slate, storage-\*, storage-azure, storage-gcs, storage-uploadthing, storage-vercel-blob, storage-s3, translations, ui, templates, examples(\/(\w|-)+)?, deps
-- Scopes should be chosen based upon the package(s) being modified. If multiple packages are being modified, choose the most relevant one or no scope at all.
-- Example PR titles:
-  - `feat(db-mongodb): add support for transactions`
-  - `feat(richtext-lexical): add options to hide block handles`
-  - `fix(ui): json field type ignoring editorOptions`
-
-## Commit Guidelines
-
-- This repository follows conventional commits for commit messages
-- The first commit of a branch should follow the PR title format: <type>(<scope>): <title>. Follow the same rules as PR titles.
-- Subsequent commits should prefer `chore` commits without a scope unless a specific package is being modified.
-- These will eventually be squashed into the first commit when merging the PR.
diff --git a/AGENTS.md b/AGENTS.md
new file mode 120000
index 00000000000..681311eb9cf
--- /dev/null
+++ b/AGENTS.md
@@ -0,0 +1 @@
+CLAUDE.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
deleted file mode 120000
index 47dc3e3d863..00000000000
--- a/CLAUDE.md
+++ /dev/null
@@ -1 +0,0 @@
-AGENTS.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
new file mode 100644
index 00000000000..04182b747af
--- /dev/null
+++ b/CLAUDE.md
@@ -0,0 +1,135 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Project Structure
+
+Payload is a monorepo structured around Next.js, containing the core CMS platform, database adapters, plugins, and tooling.
+
+### Key Directories
+
+- `packages/` - All publishable packages
+  - `packages/payload` - Core Payload package containing the main CMS logic
+  - `packages/ui` - Admin UI components (React Server Components)
+  - `packages/next` - Next.js integration layer
+  - `packages/db-*` - Database adapters (MongoDB, Postgres, SQLite, Vercel Postgres, D1 SQLite)
+  - `packages/drizzle` - Drizzle ORM integration
+  - `packages/richtext-*` - Rich text editors (Lexical, Slate)
+  - `packages/storage-*` - Storage adapters (S3, Azure, GCS, Uploadthing, Vercel Blob)
+  - `packages/email-*` - Email adapters (Nodemailer, Resend)
+  - `packages/plugin-*` - Additional functionality plugins
+  - `packages/graphql` - GraphQL API layer
+  - `packages/translations` - i18n translations
+- `test/` - Test suites organized by feature area. Each directory contains a granular Payload config and test files
+- `docs/` - Documentation (deployed to payloadcms.com)
+- `tools/` - Monorepo tooling
+- `templates/` - Production-ready project templates
+- `examples/` - Example implementations
+
+### Architecture Notes
+
+- Payload 3.x is built as a Next.js native CMS that installs directly in `/app` folder
+- UI is built with React Server Components (RSC)
+- Database adapters use Drizzle ORM under the hood
+- Packages use TypeScript with strict mode and path mappings defined in `tsconfig.base.json`
+- Source files are in `src/`, compiled outputs go to `dist/`
+- Monorepo uses pnpm workspaces and Turbo for builds
+
+## Build Commands
+
+- `pnpm install` - Install all dependencies (pnpm required - run `corepack enable` first)
+- `pnpm build` or `pnpm build:core` - Build core packages (excludes plugins and storage adapters)
+- `pnpm build:all` - Build all packages
+- `pnpm build:<directory_name>` - Build specific package (e.g. `pnpm build:db-mongodb`, `pnpm build:ui`)
+
+## Development
+
+### Running Dev Server
+
+- `pnpm dev` - Start dev server with default config (`test/_community/config.ts`)
+- `pnpm dev <directory_name>` - Start dev server with specific test config (e.g. `pnpm dev fields` loads `test/fields/config.ts`)
+- `pnpm dev:postgres` - Run dev server with Postgres
+- `pnpm dev:memorydb` - Run dev server with in-memory MongoDB
+
+### Development Environment
+
+- Auto-login is enabled by default with credentials: `dev@payloadcms.com` / `test`
+- To disable: pass `--no-auto-login` flag or set `PAYLOAD_PUBLIC_DISABLE_AUTO_LOGIN=false`
+- Default database is MongoDB (in-memory). Switch to Postgres with `PAYLOAD_DATABASE=postgres`
+- Docker services: `pnpm docker:start` / `pnpm docker:stop` / `pnpm docker:restart`
+
+## Testing
+
+### Running Tests
+
+- `pnpm test` - Run all tests (integration + components + e2e)
+- `pnpm test:int` - Run integration tests (MongoDB, recommended for verifying local changes)
+- `pnpm test:int <directory_name>` - Run specific integration test suite (e.g. `pnpm test:int fields`)
+- `pnpm test:int:postgres` - Run integration tests with Postgres
+- `pnpm test:int:sqlite` - Run integration tests with SQLite
+- `pnpm test:unit` - Run unit tests
+- `pnpm test:e2e` - Run end-to-end tests (Playwright)
+- `pnpm test:e2e:headed` - Run e2e tests in headed mode
+- `pnpm test:e2e:debug` - Run e2e tests in debug mode
+- `pnpm test:components` - Run component tests (Jest)
+- `pnpm test:types` - Run type tests (tstyche)
+
+### Test Structure
+
+Each test directory in `test/` follows this pattern:
+
+```
+test/<feature-name>/
+├── config.ts        # Lightweight Payload config for testing
+├── int.spec.ts      # Integration tests (Jest)
+├── e2e.spec.ts      # End-to-end tests (Playwright)
+└── payload-types.ts # Generated types
+```
+
+Generate types for a test directory: `pnpm dev:generate-types <directory_name>`
+
+## Linting & Formatting
+
+- `pnpm lint` - Run linter across all packages
+- `pnpm lint:fix` - Fix linting issues
+
+## Internationalization
+
+- Translation files are in `packages/translations/src/languages/`
+- Add new strings to English locale first, then translate to other languages
+- Run `pnpm translateNewKeys` to auto-translate new keys (requires `OPENAI_KEY` in `.env`)
+- Lexical translations: `cd packages/richtext-lexical && pnpm translateNewKeys`
+
+## Commit & PR Guidelines
+
+This repository follows [Conventional Commits](https://www.conventionalcommits.org/).
+
+### PR Title Format
+
+`<type>(<scope>): <title>`
+
+- Title must start with lowercase letter
+- Types: `build`, `chore`, `ci`, `docs`, `examples`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `templates`, `test`
+- Prefer `feat` for new features, `fix` for bug fixes
+- Scopes match package names: `db-*`, `richtext-*`, `storage-*`, `plugin-*`, `ui`, `next`, `graphql`, `translations`, etc.
+- Choose most relevant scope if multiple packages modified, or omit scope entirely
+
+Examples:
+
+- `feat(db-mongodb): add support for transactions`
+- `feat(richtext-lexical): add options to hide block handles`
+- `fix(ui): json field type ignoring editorOptions`
+- `feat: add new collection functionality`
+
+### Commit Guidelines
+
+- First commit of branch should follow PR title format
+- Subsequent commits should use `chore` without scope unless specific package is being modified
+- All commits in a PR are squashed on merge using PR title as commit message
+
+## Additional Resources
+
+- LLMS.txt: <https://payloadcms.com/llms.txt>
+- LLMS-FULL.txt: <https://payloadcms.com/llms-full.txt>
+- Node version: ^18.20.2 || >=20.9.0
+- pnpm version: ^9.7.0

PATCH

echo "Patch applied successfully."
