#!/usr/bin/env bash
set -euo pipefail

cd /workspace/saleor-dashboard

# Idempotency guard
if grep -qF "- `npm run dev` - Start development server on port 9000 with host binding, ALWAY" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -8,22 +8,23 @@ Saleor Dashboard is a GraphQL-powered, single-page React application built with
 
 ### Basic Development
 
-- `npm run dev` - Start development server on port 9000 with host binding
-- `npm run build` - Build production bundle with 8GB memory allocation
+- `npm run dev` - Start development server on port 9000 with host binding, ALWAYS run this process in background, if you can't do that ask user
+- `npm run build` - Build production bundle
 - `npm run preview` - Preview production build locally
 
 ### Code Quality & Testing
 
+Before completing changes make sure you run these commands:
+
 - `npm run lint` - Run ESLint with auto-fix on src/ and playwright/ directories
-- `npm run test` - Run Jest tests for src/ directory
-- `npm run test:ci` - Run tests with coverage report
-- `npm run check-types` - Run TypeScript type checking for both src and playwright
-- `npm run check-types:src` - Type check src/ directory with strict plugin
-- `npm run check-types:playwright` - Type check playwright test files
+- `./node_modules/.bin/jest <file_path>` - Run specific test file (recommended for local development, running all tests is slow)
+- `npm run check-types` - Run TypeScript type checking
+- `npm run format:check` - Format files using prettier
+- `npm run knip` - Check for unused files/dependencies/exports
 
 ### GraphQL & Code Generation
 
-- `npm run generate` - Generate GraphQL types and hooks from schema
+- `npm run generate` - Generate GraphQL types and hooks, after making changes in queries/mutations or updating schema
 - `npm run fetch-schema` - Download GraphQL schema from Saleor repository
 - `npm run fetch-local-schema` - Fetch schema from local Saleor instance
 
@@ -119,3 +120,62 @@ The codebase follows a feature-based architecture with shared components:
 - Ensure type safety with TypeScript strict plugin
 
 Add // Arrange // Act // Assert comments in tests to clarify test structure
+
+## Git Conflict Resolution
+
+### Auto-generated Files (DO NOT manually resolve)
+
+These files should be regenerated after resolving source conflicts:
+
+- `package-lock.json` - Run `npm install` after resolving `package.json`
+- `src/graphql/hooks.generated.ts` - Run `npm run generate` after resolving GraphQL files
+- `src/graphql/typePolicies.generated.ts` - Run `npm run generate` after resolving GraphQL files
+- `src/graphql/fragmentTypes.generated.ts` - Run `npm run generate` after resolving GraphQL files
+- `src/graphql/types.generated.ts` - Run `npm run generate` after resolving GraphQL files
+
+### Package Version Conflicts
+
+Always use the latest version when resolving package version conflicts between branches.
+
+## Backend Integration
+
+This frontend connects to a Saleor GraphQL backend:
+
+- Default backend URL: http://localhost:8000/graphql/
+- Configure via environment variables (see `docs/configuration.md`)
+- Default development credentials for local Saleor instance: `admin@example.com` / `admin`
+- Use `npm run fetch-local-schema` to sync GraphQL schema from local backend
+
+## Package Updates
+
+When modifying `package.json`, always run `npm install` to update `package-lock.json` and node_modules.
+
+## Contributing
+
+### Changesets
+
+Use changesets CLI for user-facing changes that should appear in the changelog:
+
+**Include in changesets:**
+
+- Features: Provide detailed description with examples/screenshots
+- Enhancements: Concise description of the improvement
+- Bug fixes: Describe what didn't work → what works now
+
+**Skip changesets for:**
+
+- Internal refactors
+- Code style changes
+- Test additions
+- CI/CD changes
+- Documentation updates (unless user-facing)
+
+### Pull Request Guidelines
+
+PR descriptions should:
+
+- Provide context for reviewers to understand the changes
+- Explain non-obvious decisions or trade-offs
+- Focus on the "why" rather than the "what" (code shows what)
+- Include screenshots for UI changes
+- Reference related issues or discussions
PATCH

echo "Gold patch applied."
