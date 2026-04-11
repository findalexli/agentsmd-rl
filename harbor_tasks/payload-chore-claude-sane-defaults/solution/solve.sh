#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if grep -q 'packages/kv-redis' CLAUDE.md 2>/dev/null && [ -f .claude/hooks/post-edit.sh ]; then
    echo "Patch already applied."
    exit 0
fi

# Create .claude directories
mkdir -p .claude/hooks

# Create post-edit.sh hook
cat > .claude/hooks/post-edit.sh <<'HOOK'
#!/bin/bash

# Post-edit hook to format files after creating/editing
# This is the bash equivalent of lint-staged in package.json

# To test this file directly via cli:
# echo '{"tool_input": {"file_path": "path/to/your/file"}}' | .claude/hooks/post-edit.sh

# Read JSON from stdin and extract file path
FILE=$(jq -r '.tool_input.file_path' 2>/dev/null)

if [ -z "$FILE" ] || [ "$FILE" = "null" ]; then
  exit 0
fi

# Check if file exists
if [ ! -f "$FILE" ]; then
  exit 0
fi

# Format based on file type
case "$FILE" in
  */package.json)
    npx sort-package-json "$FILE" 2>/dev/null
    ;;
  *.yml|*.json)
    npx prettier --write "$FILE" 2>/dev/null
    ;;
  *.md|*.mdx)
    npx prettier --write "$FILE" 2>/dev/null
    if command -v markdownlint >/dev/null 2>&1; then
      markdownlint -i node_modules "$FILE" 2>/dev/null
    fi
    ;;
  *.js|*.jsx|*.ts|*.tsx)
    npx prettier --write "$FILE" 2>/dev/null
    npx eslint --cache --fix "$FILE" 2>/dev/null
    ;;
esac

exit 0
HOOK
chmod +x .claude/hooks/post-edit.sh

# Create .claude/settings.json
cat > .claude/settings.json <<'SETTINGS'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/post-edit.sh"
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(gh issue view:*)",
      "Bash(gh pr view:*)",
      "Bash(gh release view:*)",
      "Bash(gh run list:*)",
      "Bash(gh run view:*)",
      "Bash(git branch:*)",
      "Bash(git describe:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(git ls-files:*)",
      "Bash(git remote:*)",
      "Bash(git rev-parse:*)",
      "Bash(git show:*)",
      "Bash(git status)",
      "Bash(pnpm --version)",
      "Bash(pnpm audit:*)",
      "Bash(pnpm install)",
      "Bash(pnpm list:*)",
      "Bash(pnpm run:*)",
      "Bash(pnpm turbo:*)",
      "Bash(pnpm view:*)",
      "Bash(pnpm why:*)",
      "Bash(pwd)",
      "Bash(which:*)",
      "WebFetch(domain:docs.aws.amazon.com)",
      "WebFetch(domain:docs.claude.com)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:payloadcms.com)",
      "WebFetch(domain:pure.md)",
      "WebFetch(domain:raw.githubusercontent.com)",
      "WebFetch(domain:www.anthropic.com)",
      "WebFetch(domain:www.npmjs.com)",
      "WebSearch"
    ]
  }
}
SETTINGS

# Update CLAUDE.md with git apply
git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 04182b747af..eaccd7d5caa 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -14,8 +14,9 @@ Payload is a monorepo structured around Next.js, containing the core CMS platfor
   - `packages/next` - Next.js integration layer
   - `packages/db-*` - Database adapters (MongoDB, Postgres, SQLite, Vercel Postgres, D1 SQLite)
   - `packages/drizzle` - Drizzle ORM integration
+  - `packages/kv-redis` - Redis key-value store adapter
   - `packages/richtext-*` - Rich text editors (Lexical, Slate)
-  - `packages/storage-*` - Storage adapters (S3, Azure, GCS, Uploadthing, Vercel Blob)
+  - `packages/storage-*` - Storage adapters (S3, Azure, GCS, Uploadthing, Vercel Blob, R2)
   - `packages/email-*` - Email adapters (Nodemailer, Resend)
   - `packages/plugin-*` - Additional functionality plugins
   - `packages/graphql` - GraphQL API layer
@@ -35,21 +36,28 @@ Payload is a monorepo structured around Next.js, containing the core CMS platfor
 - Source files are in `src/`, compiled outputs go to `dist/`
 - Monorepo uses pnpm workspaces and Turbo for builds

+## Quick Start
+
+1. `pnpm install`
+2. `pnpm run build:core`
+3. `pnpm run dev` (MongoDB) or `pnpm run dev:postgres`
+
 ## Build Commands

-- `pnpm install` - Install all dependencies (pnpm required - run `corepack enable` first)
-- `pnpm build` or `pnpm build:core` - Build core packages (excludes plugins and storage adapters)
-- `pnpm build:all` - Build all packages
-- `pnpm build:<directory_name>` - Build specific package (e.g. `pnpm build:db-mongodb`, `pnpm build:ui`)
+- `pnpm install` - Install all dependencies
+- `pnpm turbo` - All Turbo commands should be run from root with pnpm - not with `turbo` directly
+- `pnpm run build` or `pnpm run build:core` - Build core packages (excludes plugins and storage adapters)
+- `pnpm run build:all` - Build all packages
+- `pnpm run build:<directory_name>` - Build specific package (e.g. `pnpm run build:db-mongodb`, `pnpm run build:ui`)

 ## Development

 ### Running Dev Server

-- `pnpm dev` - Start dev server with default config (`test/_community/config.ts`)
-- `pnpm dev <directory_name>` - Start dev server with specific test config (e.g. `pnpm dev fields` loads `test/fields/config.ts`)
-- `pnpm dev:postgres` - Run dev server with Postgres
-- `pnpm dev:memorydb` - Run dev server with in-memory MongoDB
+- `pnpm run dev` - Start dev server with default config (`test/_community/config.ts`)
+- `pnpm run dev <directory_name>` - Start dev server with specific test config (e.g. `pnpm run dev fields` loads `test/fields/config.ts`)
+- `pnpm run dev:postgres` - Run dev server with Postgres
+- `pnpm run dev:memorydb` - Run dev server with in-memory MongoDB

 ### Development Environment

@@ -60,19 +68,12 @@ Payload is a monorepo structured around Next.js, containing the core CMS platfor

 ## Testing

-### Running Tests
-
-- `pnpm test` - Run all tests (integration + components + e2e)
-- `pnpm test:int` - Run integration tests (MongoDB, recommended for verifying local changes)
-- `pnpm test:int <directory_name>` - Run specific integration test suite (e.g. `pnpm test:int fields`)
-- `pnpm test:int:postgres` - Run integration tests with Postgres
-- `pnpm test:int:sqlite` - Run integration tests with SQLite
-- `pnpm test:unit` - Run unit tests
-- `pnpm test:e2e` - Run end-to-end tests (Playwright)
-- `pnpm test:e2e:headed` - Run e2e tests in headed mode
-- `pnpm test:e2e:debug` - Run e2e tests in debug mode
-- `pnpm test:components` - Run component tests (Jest)
-- `pnpm test:types` - Run type tests (tstyche)
+- `pnpm run test` - Run all tests (integration + components + e2e)
+- `pnpm run test:int` - Integration tests (MongoDB, recommended)
+- `pnpm run test:int <dir>` - Specific test suite (e.g. `fields`)
+- `pnpm run test:int:postgres|sqlite` - Integration tests with other databases
+- `pnpm run test:e2e` - Playwright tests (add `:headed` or `:debug` suffix)
+- `pnpm run test:unit|components|types` - Other test suites

 ### Test Structure

@@ -86,19 +87,19 @@ test/<feature-name>/
 └── payload-types.ts # Generated types
 ```

-Generate types for a test directory: `pnpm dev:generate-types <directory_name>`
+Generate types for a test directory: `pnpm run dev:generate-types <directory_name>`

 ## Linting & Formatting

-- `pnpm lint` - Run linter across all packages
-- `pnpm lint:fix` - Fix linting issues
+- `pnpm run lint` - Run linter across all packages
+- `pnpm run lint:fix` - Fix linting issues

 ## Internationalization

 - Translation files are in `packages/translations/src/languages/`
 - Add new strings to English locale first, then translate to other languages
-- Run `pnpm translateNewKeys` to auto-translate new keys (requires `OPENAI_KEY` in `.env`)
-- Lexical translations: `cd packages/richtext-lexical && pnpm translateNewKeys`
+- Run `pnpm run translateNewKeys` to auto-translate new keys (requires `OPENAI_KEY` in `.env`)
+- Lexical translations: `cd packages/richtext-lexical && pnpm run translateNewKeys`

 ## Commit & PR Guidelines

PATCH

echo "Patch applied successfully."
