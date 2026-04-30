#!/usr/bin/env bash
set -euo pipefail

cd /workspace/arkenv

# Idempotency guard
if grep -qF "This project is built on [ArkType](https://arktype.io/), TypeScript's 1:1 valida" ".cursor/rules/arktype.mdc" && grep -qF "This project uses [Biome](https://biomejs.dev/) for formatting and linting. The " ".cursor/rules/coding-guidelines.mdc" && grep -qF "- `packages/arkenv` should not depend on other workspace packages" ".cursor/rules/monorepo.mdc" && grep -qF "Certain dependencies are configured to use `onlyBuiltDependencies` in `pnpm.only" ".cursor/rules/pnpm.mdc" && grep -qF "**Test behavior, not aesthetics.** Focus on what users can do and what the compo" ".cursor/rules/test-patterns.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/arktype.mdc b/.cursor/rules/arktype.mdc
@@ -0,0 +1,87 @@
+---
+description: ArkType-specific patterns and conventions
+globs:
+  - "packages/arkenv/**/*.ts"
+alwaysApply: false
+---
+
+# ArkType Patterns
+
+This project is built on [ArkType](https://arktype.io/), TypeScript's 1:1 validator.
+
+## Core Concepts
+
+- Use ArkType's `type()` function to define schemas
+- Leverage ArkType's type inference for TypeScript types
+- Use the scoped `$` type system for custom types (see `scope.ts`)
+
+## Schema Definition
+
+Define environment variable schemas using ArkType syntax:
+
+```typescript
+import { type } from "arktype";
+
+const env = createEnv({
+  HOST: "string.host", // Custom host type
+  PORT: "number.port", // Custom port type
+  NODE_ENV: "'development' | 'production' | 'test'", // Union type
+});
+```
+
+## Type Validation
+
+- ArkType validates at runtime
+- TypeScript types are inferred from the schema
+- Invalid values throw `ArkEnvError`
+
+## Custom Types
+
+Custom types are defined in `scope.ts` using ArkType's scoped type system:
+
+```typescript
+import { $ } from "./scope";
+
+// Custom types are defined using $ and available as:
+// "string.host", "number.port", etc.
+```
+
+## Type Inference
+
+- Use `type.infer` to extract TypeScript types from schemas
+- The return type of `createEnv` is inferred from the schema
+- No manual type definitions needed
+
+## Error Handling
+
+- ArkType returns `type.errors` for validation failures
+- Convert to `ArkEnvError` for user-friendly messages
+- Error messages include variable name and expected type
+
+## Best Practices
+
+- Keep schemas readable and TypeScript-like
+- Use union types for enums (e.g., `"'dev' | 'prod'"`)
+- Leverage ArkType's built-in types where possible
+- Custom types should be defined in `scope.ts` for reusability
+
+## Example
+
+```typescript
+import arkenv from "arkenv";
+
+const env = arkenv({
+  HOST: "string.host",
+  PORT: "number.port",
+  NODE_ENV: "'development' | 'production' | 'test'",
+  DEBUG: "boolean",
+  TIMEOUT: "number >= 0",
+});
+
+// TypeScript knows the exact types:
+// env.HOST: string (validated as host)
+// env.PORT: number (validated as port 0-65535)
+// env.NODE_ENV: "development" | "production" | "test"
+// env.DEBUG: boolean
+// env.TIMEOUT: number (>= 0)
+```
diff --git a/.cursor/rules/coding-guidelines.mdc b/.cursor/rules/coding-guidelines.mdc
@@ -0,0 +1,72 @@
+---
+description: Coding guidelines and standards for ArkEnv
+globs:
+  - "**/*.ts"
+  - "**/*.tsx"
+alwaysApply: true
+---
+
+# Coding Guidelines
+
+## TypeScript
+
+- Prefer `type` over `interface` for type definitions
+- Use TypeScript 5.1+ features when appropriate
+- Leverage `const` type parameters for better inference
+- Use JSDoc comments for public APIs
+
+## Code Style
+
+This project uses [Biome](https://biomejs.dev/) for formatting and linting. The configuration is in `biome.jsonc`.
+
+### Key Style Rules
+
+- **Indentation**: Use tabs (not spaces)
+- **Quotes**: Use double quotes for strings
+- **Imports**: Organize imports automatically (Biome handles this)
+- **Types**: Use `type` instead of `interface`
+- **Type inference**: Avoid explicit types when TypeScript can infer them (`noInferrableTypes` error)
+- **Const assertions**: Use `as const` where appropriate (`useAsConstAssertion` error)
+
+### Linting Rules
+
+- **Parameter assignment**: Don't reassign function parameters (`noParameterAssign` error)
+- **Const assertions**: Always use `as const` for immutable values (`useAsConstAssertion` error)
+- **Default parameters**: Place default parameters last (`useDefaultParameterLast` error)
+- **Enums**: Always initialize enum values (`useEnumInitializers` error)
+- **Self-closing elements**: Use self-closing JSX elements (`useSelfClosingElements` error)
+- **Single variable declarations**: Declare one variable per statement (`useSingleVarDeclarator` error)
+- **Unused template literals**: Avoid unnecessary template literals (`noUnusedTemplateLiteral` error)
+- **Number namespace**: Prefer `Number.parseInt` over global `parseInt` (`useNumberNamespace` error)
+- **Console usage**: Console usage is a warning (allowed in `bin/` and examples/playgrounds)
+
+## File Organization
+
+- Co-locate tests: `Component.tsx` next to `Component.test.tsx`
+- Use barrel exports (`index.ts`) for package entry points
+- Keep files focused and single-purpose
+
+## Naming Conventions
+
+- **Files**: Use kebab-case for files (`create-env.ts`)
+- **Functions**: Use camelCase (`createEnv`)
+- **Types**: Use PascalCase (`ArkEnvError`)
+- **Constants**: Use UPPER_SNAKE_CASE for environment variables and constants
+
+## Documentation
+
+- Use JSDoc comments for public APIs
+- Include examples in JSDoc when helpful
+- Document complex type logic
+
+## Error Handling
+
+- Use `ArkEnvError` for environment variable validation errors
+- Provide clear, actionable error messages
+- Include the variable name and expected type in errors
+
+## Performance
+
+- Keep bundle size small (< 1kB gzipped goal)
+- Avoid unnecessary dependencies
+- Prefer tree-shakeable exports
diff --git a/.cursor/rules/monorepo.mdc b/.cursor/rules/monorepo.mdc
@@ -0,0 +1,101 @@
+---
+description: Monorepo structure and conventions
+globs:
+  - "**/package.json"
+  - "turbo.json"
+alwaysApply: true
+---
+
+# Monorepo Guidelines
+
+This is a pnpm + Turborepo monorepo.
+
+## Directory Structure
+
+```
+arkenv/
+├── packages/          # Published npm packages
+│   ├── arkenv/       # Core package
+│   └── vite-plugin/  # Vite plugin package
+├── apps/             # Applications
+│   ├── www/          # Documentation site (Next.js)
+│   └── playgrounds/  # Playground apps for testing
+├── examples/         # Example projects
+├── tooling/          # Development tools (not published)
+└── turbo.json        # Turborepo configuration
+```
+
+## Package Types
+
+### Published Packages (`packages/`)
+- These are published to npm
+- Require changesets for versioning
+- Must have proper exports and types
+- Examples: `arkenv`, `@arkenv/vite-plugin`
+
+### Applications (`apps/`)
+- Not published to npm
+- May depend on workspace packages
+- Examples: `www`, `playgrounds/*`
+
+### Examples (`examples/`)
+- Standalone example projects
+- Not published
+- May have their own lock files
+- Used as test fixtures
+
+### Tooling (`tooling/`)
+- Development and testing tools
+- Not published to npm
+- Excluded from changesets
+- Examples: `playwright-www`
+
+## Turborepo
+
+Tasks are defined in `turbo.json`. Common tasks:
+- `build` - Build packages
+- `dev` - Development mode
+- `typecheck` - Type checking
+- `test` - Run tests
+- `test:e2e` - End-to-end tests
+
+## Filtering
+
+Use Turborepo filters to run tasks on specific packages:
+
+```bash
+# Run build for specific package
+turbo run build --filter=arkenv
+
+# Run tests for all packages
+turbo run test --filter=./packages/*
+
+# Run for package and its dependencies
+turbo run build --filter=www...
+```
+
+## Changesets
+
+- Published packages require changesets
+- Create changeset with: `pnpm changeset`
+- Changesets are in `.changeset/` directory
+- Examples and tooling don't need changesets
+
+## Dependencies Between Packages
+
+- Use `workspace:*` protocol for workspace dependencies
+- `packages/arkenv` should not depend on other workspace packages
+- `packages/vite-plugin` depends on `arkenv`
+- `apps/www` may depend on workspace packages
+
+## Build Output
+
+- Package builds go to `dist/` directory
+- Build output should be gitignored
+- Source files are in `src/` directory
+
+## Publishing
+
+- Only packages in `packages/` are published
+- Publishing is handled by changesets
+- Run `pnpm release` to publish after merging PRs
diff --git a/.cursor/rules/pnpm.mdc b/.cursor/rules/pnpm.mdc
@@ -0,0 +1,75 @@
+---
+description: pnpm package manager guidelines
+globs:
+  - "**/package.json"
+  - "pnpm-lock.yaml"
+  - "pnpm-workspace.yaml"
+alwaysApply: true
+---
+
+# pnpm Guidelines
+
+This monorepo uses **pnpm** as the package manager.
+
+## Package Manager
+
+- Always use `pnpm` for all package management operations
+- Never use `npm` or `yarn` commands
+- The project uses `pnpm@10.20.0` (specified in `packageManager` field)
+
+## Common Commands
+
+```bash
+# Install dependencies
+pnpm install
+
+# Add a dependency to a workspace package
+pnpm add <package> --filter <workspace-name>
+
+# Add a dev dependency
+pnpm add -D <package> --filter <workspace-name>
+
+# Run a script in a specific package
+pnpm --filter <workspace-name> <script>
+
+# Run a script across all packages
+pnpm run <script>
+```
+
+## Workspace Structure
+
+This is a pnpm workspace monorepo. Packages are defined in:
+- `packages/` - Published npm packages
+- `apps/` - Applications (www, playgrounds)
+- `tooling/` - Development tools (not published)
+- `examples/` - Example projects
+
+## Workspace Protocol
+
+When referencing workspace packages, use the `workspace:*` protocol:
+
+```json
+{
+  "dependencies": {
+    "arkenv": "workspace:*"
+  }
+}
+```
+
+## Only Built Dependencies
+
+Certain dependencies are configured to use `onlyBuiltDependencies` in `pnpm.onlyBuiltDependencies`. These are typically native dependencies that need special handling:
+
+- `@biomejs/biome`
+- `@sentry/cli`
+- `@swc/core`
+- `@tailwindcss/oxide`
+- `@vercel/speed-insights`
+- `esbuild`
+- `sharp`
+
+## Lock File
+
+- Always commit `pnpm-lock.yaml`
+- Never manually edit the lock file
+- Run `pnpm install` to update the lock file when dependencies change
diff --git a/.cursor/rules/test-patterns.mdc b/.cursor/rules/test-patterns.mdc
@@ -0,0 +1,149 @@
+---
+description: Testing patterns and guidelines
+globs:
+  - "**/*.test.ts"
+  - "**/*.test.tsx"
+  - "**/__tests__/**/*.ts"
+  - "**/__tests__/**/*.tsx"
+alwaysApply: true
+---
+
+# Test Patterns
+
+## Testing Philosophy
+
+**"Examples as Test Fixtures"** - Examples serve dual purposes:
+1. **Documentation** - Show real-world usage patterns
+2. **Test Fixtures** - Provide real projects to test against
+
+**"Test the User Journey"** - End-to-end tests validate complete user workflows in real applications.
+
+## Test Structure
+
+### Unit Tests (`packages/arkenv/src/*.test.ts`)
+- Test individual functions and edge cases
+- Validate error handling and type checking
+- Fast, isolated tests for core logic
+- Co-locate with source: `create-env.ts` → `create-env.test.ts`
+
+### Integration Tests (`packages/vite-plugin/src/*.test.ts`)
+- Test the vite plugin using the `with-vite-react-ts` example as a fixture
+- Validate that the plugin works with real Vite projects
+- Use fixture-based testing pattern (see `__fixtures__` directory)
+
+### End-to-End Tests (`tooling/playwright-www/`)
+- Test complete user workflows in the www application
+- Validate real browser behavior across Chromium, Firefox, and WebKit
+- Focus on user-facing behavior, not implementation details
+
+## Component Testing (www app)
+
+**Test behavior, not aesthetics.** Focus on what users can do and what the component guarantees through its API.
+
+### What We Test
+- **Public API** - props, events, and component contract
+- **User behavior** - clicks, typing, focus, keyboard, ARIA
+- **State transitions** - loading, success, error, disabled states
+- **Accessibility** - focus order, keyboard activation, aria attributes
+- **Side effects** - UI changes that affect user experience
+
+### What We Don't Test
+- Pure styling or CSS classes
+- Library internals (Radix/shadcn)
+- Implementation details (hooks, setState, private variables)
+- Visual variants (use Storybook instead)
+
+## Test Framework
+
+- Use **Vitest** for unit and integration tests
+- Use **Playwright** for end-to-end tests
+- Use **Testing Library** for component tests (with `user-event` for real user simulation)
+
+## Test Patterns
+
+### Unit Test Example
+
+```typescript
+import { describe, expect, it } from "vitest";
+import { createEnv } from "./create-env";
+
+describe("createEnv", () => {
+  it("should validate string env variables", () => {
+    process.env.TEST_STRING = "hello";
+    const env = createEnv({
+      TEST_STRING: "string",
+    });
+    expect(env.TEST_STRING).toBe("hello");
+  });
+});
+```
+
+### Fixture-Based Integration Test Example
+
+```typescript
+import { readdirSync } from "node:fs";
+import { join } from "node:path";
+import { describe } from "vitest";
+
+const fixturesDir = join(__dirname, "__fixtures__");
+
+for (const name of readdirSync(fixturesDir)) {
+  describe(`Fixture: ${name}`, () => {
+    // Test each fixture
+  });
+}
+```
+
+### Component Test Example
+
+```typescript
+import { render, screen } from "@testing-library/react";
+import userEvent from "@testing-library/user-event";
+import { describe, expect, it } from "vitest";
+import { Component } from "./component";
+
+describe("Component", () => {
+  it("should handle user interaction", async () => {
+    const user = userEvent.setup();
+    render(<Component />);
+    
+    const button = screen.getByRole("button", { name: /submit/i });
+    await user.click(button);
+    
+    expect(screen.getByText("Success")).toBeInTheDocument();
+  });
+});
+```
+
+## Running Tests
+
+```bash
+# Run all tests
+pnpm test -- --run
+
+# Run specific package tests
+pnpm test --project arkenv -- --run
+pnpm test --project vite-plugin -- --run
+
+# Run end-to-end tests
+pnpm run test:e2e
+
+# Run e2e with UI
+pnpm run test:e2e:ui
+```
+
+## Test Organization
+
+- Keep tests fast, deterministic, and parallelizable
+- Mock at component boundaries (network, time, context)
+- Query by role, name, label, and text (accessibility first)
+- Use `beforeEach`/`afterEach` for cleanup, not `beforeAll`/`afterAll` when possible
+
+## Coverage Goals
+
+- ✅ Environment variable parsing and validation
+- ✅ Type checking and error handling
+- ✅ Default value handling
+- ✅ Custom type validation (host, port, etc.)
+- ✅ Plugin integration with Vite
+- ✅ Real project build testing using examples as fixtures
PATCH

echo "Gold patch applied."
