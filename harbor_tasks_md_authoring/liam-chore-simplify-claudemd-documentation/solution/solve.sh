#!/usr/bin/env bash
set -euo pipefail

cd /workspace/liam

# Idempotency guard
if grep -qF "- **Let the code speak** \u2013 If you need a multi-paragraph comment, refactor until" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,69 +2,35 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
-## Project Overview
-
-Liam ERD is a database schema visualization tool that generates beautiful, interactive ER diagrams. The project consists of a web application, CLI tool, and multiple supporting packages in a pnpm monorepo structure.
-
 ## Essential Commands
 
-### Development
-```bash
-# Start development servers
-pnpm dev
-
-# Build all packages
-pnpm build
+- pnpm dev - Start dev servers
+- cd frontend/apps/app && pnpm dev - Start dev server for specific package
+- pnpm build - Build all packages
+- pnpm lint - Run linting and formatting
+- pnpm test - Run tests
+- pnpm fmt - Run format code
 
-# Run linting and formatting
-pnpm lint
-pnpm fmt
+### App-specific Commands
 
-# Run tests
-pnpm test
-pnpm test:e2e
-
-# Generate code and CSS type definitions
-pnpm gen:turbo
-```
-
-### App-specific Development
-```bash
+````bash
 # Run only the main web app (port 3001)
-cd frontend/apps/app && pnpm dev
-
-# Run with CSS generation
-cd frontend/apps/app && pnpm dev:css
+pnpm --filter @liam-hq/app dev
 
-# Type checking
-cd frontend/apps/app && pnpm lint:tsc
-```
+# Format code
+pnpm --filter @liam-hq/agent fmt
 
-### Package Management
-```bash
-# Install dependencies
-pnpm install
-
-# Add dependency to specific package
-pnpm add <package> --filter @liam-hq/app
-
-# Run command in specific workspace
-pnpm --filter @liam-hq/cli build
-```
+# Test
+pnpm --filter @liam-hq/agent test
 
 ### Database Operations
-For database migration and type generation workflows, see [`docs/migrationOpsContext.md`](docs/migrationOpsContext.md).
 
-### Schema Changes
-- Always use the following migration workflow:
-  1. `pnpm -F db supabase:migration:new <MIGRATION_NAME>`
-  2. Write DDL in the generated migration file
-  3. `pnpm -F db supabase:migration:up` to apply changes
-  4. `pnpm -F db supabase:gen` to regenerate type definitions
+For database migration and type generation workflows, see @docs/migrationOpsContext.md.
 
 ## Architecture
 
 ### Monorepo Structure
+
 - **frontend/apps/app** - Main Next.js web application (`@liam-hq/app`)
 - **frontend/apps/docs** - Documentation site (`@liam-hq/docs`)
 - **frontend/packages/cli** - Command-line tool (`@liam-hq/cli`)
@@ -74,75 +40,76 @@ For database migration and type generation workflows, see [`docs/migrationOpsCon
 - **frontend/packages/github** - GitHub API integration (`@liam-hq/github`)
 
 ### Key Technologies
-- **Frontend**: React 18, Next.js 15, TypeScript
+
+- **Frontend**: React 19, Next.js 15, TypeScript
 - **Styling**: CSS Modules with typed definitions
 - **Visualization**: @xyflow/react (React Flow)
-- **State**: Valtio for state management
 - **Validation**: Valibot for runtime type validation
 - **Build**: Turborepo, pnpm workspaces
 
-### Data Flow
-1. Schema files are parsed by `@liam-hq/schema`
-2. ERD visualization is handled by `@liam-hq/erd-core` using React Flow
-3. UI components from `@liam-hq/ui` provide consistent design
-4. GitHub integration via `@liam-hq/github` for PR reviews
-
 ## Development Guidelines
 
+### Core Principle: **Less is more**
+
+Keep every implementation as small and obvious as possible.
+
 ### TypeScript Standards
+
 - Use runtime type validation with `valibot` for external data validation
 - Use early returns for readability
+- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious
 
 ### Code Editing
+
 - Write simple, direct code without backward compatibility concerns - update all call sites together
+
 ```typescript
 // ❌ Bad: Optional parameter leads to conditional logic
 function saveUser(data: UserData, userId?: string) {
   const id = userId || generateId(); // Unnecessary fallback logic
-  if (!userId) console.warn('Using generated ID') // Extra handling
-  return db.save(id, data)
+  if (!userId) console.warn("Using generated ID"); // Extra handling
+  return db.save(id, data);
 }
 
 // ✅ Good: Required parameter, update all callers
 function saveUser(data: UserData, userId: string) {
-  return db.save(userId, data) // Simple and clear
+  return db.save(userId, data); // Simple and clear
 }
-```
+````
 
 ### Component Patterns
+
 - Use named exports only (no default exports)
 - Event handlers should be prefixed with "handle" (e.g., `handleClick`)
 - Use CSS Modules for all styling
 - Import UI components from `@liam-hq/ui` when available
 - Import icons from `@liam-hq/ui`
 
 ### File Organization
+
 - Don't code directly in `page.tsx` - create separate page components
 - Follow existing import patterns and tsconfig paths
 - Use consts instead of functions: `const toggle = () => {}`
 
 ### Data Fetching
+
 - Server Components for server-side data fetching
 - Client-side fetching only when necessary
 - Align data fetching responsibilities with component roles
 - Use Server Actions for all data mutations (create, update, delete operations)
 
 ### CSS
+
 - Use CSS Variables from `@liam-hq/ui` package
 - Generate CSS type definitions with `pnpm gen:css`
-- Watch mode available with `pnpm dev:css`
 - Use CSS variables according to their intended purpose. Spacing variables should be used exclusively for margins and padding, while height and width specifications should use appropriate units (rem, px, etc.)
 
 ## Pull Requests
+
 When creating pull requests, refer to @.github/pull_request_template.md for the required information and format.
 
 ## LangGraph Development
+
 For LangGraph.js agent framework development guidance:
-- [`docs/langgraph/README.md`](docs/langgraph/README.md) - LangGraph.js complete guide
 
-## Important Files
-- `frontend/apps/docs/content/docs/contributing/repository-architecture.mdx` - Detailed package structure
-- `.cursorrules` - Contains detailed coding standards and guidelines
-- `turbo.json` - Build system configuration
-- `biome.jsonc` - Linting and formatting configuration
-- `.github/pull_request_template.md` - Pull request template
+- [`docs/langgraph/README.md`](docs/langgraph/README.md) - LangGraph.js complete guide
PATCH

echo "Gold patch applied."
