#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trpc

# Idempotency guard
if grep -qF "You are working on **tRPC** - a TypeScript-first RPC library that provides end-t" ".cursor/rules/coding-guidelines.mdc" && grep -qF "- **ALWAYS** import `createAppRouter` from `./__testHelpers` (note the different" ".cursor/rules/react-query-tests.mdc" && grep -qF "- **ALWAYS** import `testReactResource` from `./__helpers` (local to tanstack-re" ".cursor/rules/tanstack-react-query-tests.mdc" && grep -qF "- **ALWAYS** use `await using ctx = testServerAndClientResource()` for tests tha" ".cursor/rules/test-patterns.mdc" && grep -qF "- **ALWAYS** import `testReactResource` from `./test/__helpers` (note the `test/" ".cursor/rules/upgrade-tests.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/coding-guidelines.mdc b/.cursor/rules/coding-guidelines.mdc
@@ -0,0 +1,274 @@
+---
+description: tRPC coding style guidelines and conventions
+globs: ['**/*.ts', '**/*.tsx']
+alwaysApply: false
+---
+
+# tRPC Coding Guidelines
+
+## Context & Expertise Level
+
+You are working on **tRPC** - a TypeScript-first RPC library that provides end-to-end type safety between client and server. As a TypeScript expert contributing to this library, you should:
+
+- Understand advanced TypeScript concepts including conditional types, mapped types, and template literal types
+- Leverage TypeScript's inference system to its fullest potential
+- Write code that maintains tRPC's core principle: **type safety without runtime overhead**
+- Consider the developer experience of library consumers who rely on tRPC's type inference magic
+- Think about how your code affects the library's public API and type signatures
+
+This codebase pushes TypeScript to its limits to provide seamless type safety across network boundaries. Every type decision impacts thousands of developers using tRPC in production.
+
+## TypeScript & Code Style
+
+### Type Imports
+
+- **ALWAYS** use `import type` for type-only imports: `@typescript-eslint/consistent-type-imports`
+- Separate type imports from value imports
+
+```typescript
+// ✅ CORRECT
+import type { AnyRouter } from '@trpc/server';
+import { initTRPC } from '@trpc/server';
+
+// ❌ INCORRECT
+import { AnyRouter, initTRPC } from '@trpc/server';
+```
+
+### Variable Declarations
+
+- **AVOID** destructuring in most cases (project convention)
+- Prefer explicit variable assignments for better readability
+
+```typescript
+// ✅ PREFERRED (following project patterns)
+const client = ctx.client;
+const httpUrl = ctx.httpUrl;
+
+// ❌ AVOID destructuring (unless absolutely necessary)
+const { client, httpUrl } = ctx;
+```
+
+### Function Parameters
+
+- **MAXIMUM 3 parameters** per function (`max-params: 3`)
+- Use options objects for functions with many parameters
+
+```typescript
+// ✅ CORRECT
+function createClient(router: AnyRouter, opts: ClientOptions) {
+  // implementation
+}
+
+// ❌ INCORRECT - too many parameters
+function createClient(router: AnyRouter, url: string, transformer: any, links: any) {
+  // implementation
+}
+```
+
+### Naming Conventions
+
+#### Type Parameters
+
+- Use PascalCase with specific patterns: `^(T|\\$)([A-Z]([a-zA-Z]+))?[0-9]*$`
+
+```typescript
+// ✅ CORRECT
+type MyType<TRouter extends AnyRouter> = {};
+type MyType<$Router> = {};
+
+// ❌ INCORRECT
+type MyType<Router> = {};
+type MyType<router> = {};
+```
+
+#### File Names
+
+- Use camelCase for most files (`unicorn/filename-case`)
+- Exceptions: `TRPC`, `RPC`, `HTTP`, `JSON`, `.config.js`, `.d.ts`, test files, etc.
+
+#### Unused Variables
+
+- Prefix with `_` for unused variables, args, and caught errors
+
+```typescript
+// ✅ CORRECT
+function handler(_req: Request, res: Response) {
+  // _req is intentionally unused
+}
+
+try {
+  // code
+} catch (_error) {
+  // _error is intentionally unused
+}
+```
+
+### Import Patterns
+
+#### Namespace Imports
+
+- Use namespace imports for validation libraries and large modules
+
+```typescript
+// ✅ PREFERRED pattern
+import * as z from 'zod';
+import * as React from 'react';
+
+// ✅ ALSO ACCEPTABLE
+import { z } from 'zod';
+```
+
+#### Import Order (via Prettier)
+
+- Test helpers first (`___`, `__`)
+- tRPC test imports
+- Third-party modules
+- Relative imports
+
+#### Restricted Imports
+
+- **NEVER** import from `@trpc/*/src` - remove the `/src` part
+- **NEVER** use `waitFor` from Testing Library - use `vi.waitFor` instead
+- **NEVER** use `Symbol.dispose` or `Symbol.asyncDispose` - use `makeResource()` or `makeAsyncResource()`
+
+### Code Patterns
+
+#### Resource Management
+
+- **ALWAYS** use `await using` for resource cleanup
+- Use `makeResource()` and `makeAsyncResource()` instead of manual disposal
+
+```typescript
+// ✅ CORRECT
+await using ctx = testServerAndClientResource(router);
+
+// ❌ INCORRECT
+const { close } = createServer();
+try {
+  // code
+} finally {
+  await close();
+}
+```
+
+#### Error Handling
+
+- **AVOID** non-null assertions (`@typescript-eslint/no-non-null-assertion`)
+- Use proper type guards and optional chaining
+
+```typescript
+// ✅ CORRECT
+if (options && options.method) {
+  // use options.method
+}
+
+// ❌ INCORRECT
+const method = options!.method;
+```
+
+#### Console Usage
+
+- **NO** `console.log` in packages (`no-console: error` for packages)
+- Use proper logging mechanisms in package code
+- Console allowed in examples and tests
+
+### React Specific Guidelines
+
+#### Hooks
+
+- Follow React Hooks rules (`react-hooks/react-compiler`)
+- Use React Compiler compatible patterns
+
+#### Components
+
+- Use JSX runtime (no need to import React for JSX)
+- Prefer function components
+
+### Switch Statements
+
+- **ALWAYS** handle all cases (`@typescript-eslint/switch-exhaustiveness-check`)
+- Use exhaustive checking for union types
+
+### Type Safety & Inference
+
+#### Rely on TypeScript Inference
+
+- **HEAVILY RELY** on TypeScript inference rather than declaring explicit output types
+- Let TypeScript infer return types from implementation
+- Only declare types when inference is insufficient or for public APIs
+
+```typescript
+// ✅ CORRECT - Let TypeScript infer the return type
+const myProcedure = t.procedure
+  .input(z.string())
+  .query(({ input }) => {
+    return { message: `Hello ${input}` }; // Type inferred as { message: string }
+  });
+
+// ❌ AVOID - Unnecessary explicit typing
+const myProcedure = t.procedure
+  .input(z.string())
+  .query(({ input }): { message: string } => {
+    return { message: `Hello ${input}` };
+  });
+```
+
+#### When to Use Explicit Types
+
+- Public API boundaries
+- Complex generic constraints
+- When inference fails or is ambiguous
+- For documentation purposes in critical interfaces
+
+#### Inference Best Practices
+
+- Trust TypeScript's inference engine
+- Use `satisfies` operator when you need both inference and type checking
+- Leverage `as const` for literal type inference when needed
+
+```typescript
+// ✅ GOOD - Using satisfies for both inference and validation
+const config = {
+  apiVersion: 'v1',
+  timeout: 5000,
+} satisfies ApiConfig;
+
+// ✅ GOOD - Using as const for literal types
+const routes = ['users', 'posts', 'comments'] as const;
+```
+
+#### General Type Safety
+
+- Prefer explicit typing over `any` (though `any` is allowed when needed)
+- Use type assertions sparingly
+- Leverage TypeScript's strict mode features
+
+## Package-Specific Rules
+
+### Server Adapters
+
+- **AVOID** importing from `@trpc/server` in adapter code
+- Use relative imports to maintain adapter independence
+
+### Testing Files
+
+- More relaxed rules for test files
+- Non-null assertions allowed in tests
+- Unused variables allowed
+- Floating promises allowed
+
+## Code Organization
+
+### Monorepo Structure
+
+- Each package has well-defined purposes
+- Share common functionality through `@trpc/server`
+- Keep client and server concerns separate
+
+### File Structure
+
+- Use camelCase for file names
+- Group related functionality in directories
+- Use index files for clean exports
+
+This follows the established patterns in the tRPC codebase and helps maintain consistency across the monorepo.
diff --git a/.cursor/rules/react-query-tests.mdc b/.cursor/rules/react-query-tests.mdc
@@ -0,0 +1,126 @@
+---
+description: tRPC React Query (legacy) testing patterns using createAppRouter
+globs: ['packages/react-query/**/*.test.tsx']
+alwaysApply: false
+---
+
+# tRPC React Query (Legacy) Testing Patterns
+
+## Legacy React Query Specific Testing
+
+### ALWAYS use createAppRouter pattern
+
+- **ALWAYS** use `createAppRouter()` helper for legacy React Query tests
+- Import from `./__testHelpers` or create inline router with `testServerAndClientResource`
+- Uses older React Query patterns with `createTRPCReact()`
+
+### Test Resource Management
+
+```typescript
+// ✅ CORRECT: Legacy React Query pattern
+const ctx = konn()
+  .beforeEach(() => createAppRouter())
+  .afterEach((ctx) => ctx?.close?.())
+  .done();
+
+// Or inline pattern
+const { client, trpcClientOptions, close } = testServerAndClientResource(
+  appRouter,
+  {
+    server: { createContext },
+    client({ httpUrl, wssUrl }) {
+      return {
+        links: [
+          // custom link configuration
+        ],
+      };
+    },
+  },
+);
+```
+
+### Legacy React Query APIs
+
+- Use `trpc` created with `createTRPCReact<typeof appRouter>()`
+- Use `App` component wrapper with legacy Provider pattern
+- Access `queryClient`, `db`, `resolvers` from createAppRouter
+
+### Test Structure for Legacy React Query
+
+```typescript
+test('legacy react query test', async () => {
+  const { trpc, App, db } = ctx;
+
+  function MyComponent() {
+    const query = trpc.allPosts.useQuery();
+
+    return (
+      <div>
+        {query.data ? `Posts: ${query.data.length}` : 'Loading...'}
+      </div>
+    );
+  }
+
+  const utils = render(
+    <App>
+      <MyComponent />
+    </App>
+  );
+
+  await vi.waitFor(() => {
+    expect(utils.container).toHaveTextContent('Posts:');
+  });
+});
+```
+
+### Provider Setup for Legacy React Query
+
+- Uses `trpc.Provider` with legacy pattern
+- Wraps with `QueryClientProvider`
+- Custom `App` component provides both providers
+
+### Legacy Helpers Available
+
+- `createAppRouter()` - Creates full router with test data
+- `db` - Direct access to test database
+- `resolvers` - Spy functions for route calls
+- `linkSpy` - Link operation spying
+- `createContext` - Context creation spy
+
+### Import Requirements for Legacy React Query
+
+#### Test Helper Imports
+
+- **ALWAYS** import `createAppRouter` from `./__testHelpers` (note the different filename from other packages)
+- **Alternative**: Import `testServerAndClientResource` directly and create inline router
+- Path: `import { createAppRouter } from './__testHelpers';`
+- **NEVER** use `__helpers` (without 'test' prefix) - that's for other packages
+
+#### Other Required Imports
+
+- Import `createTRPCReact` from `@trpc/react-query` for legacy pattern
+- Import `konn` from `konn` for test lifecycle management
+- Import `@testing-library/react` for rendering
+- Import `getUntypedClient` from `@trpc/client`
+- Import React Query utilities for legacy patterns
+
+### Key Differences from TanStack React Query
+
+- Uses older `createTRPCReact()` pattern
+- Has built-in test database and resolvers
+- Uses `konn()` for test lifecycle
+- More complex provider setup with custom App component
+- Legacy link configuration patterns
+
+### Helper Import Comparison
+
+```typescript
+// ✅ Legacy React Query (this package)
+import { createAppRouter } from './__testHelpers'; // Note: __testHelpers
+
+// ❌ DON'T use TanStack React Query pattern
+import { testReactResource } from './__helpers'; // Wrong package
+
+// ❌ DON'T use upgrade package pattern
+import { testReactResource } from './test/__helpers'; // Wrong approach
+```
diff --git a/.cursor/rules/tanstack-react-query-tests.mdc b/.cursor/rules/tanstack-react-query-tests.mdc
@@ -0,0 +1,126 @@
+---
+description: tRPC TanStack React Query testing patterns using testReactResource
+globs: ['packages/tanstack-react-query/**/*.test.tsx']
+alwaysApply: false
+---
+
+# tRPC TanStack React Query Testing Patterns
+
+## TanStack React Query Specific Testing
+
+### ALWAYS use testReactResource from local \_\_helpers
+
+- **ALWAYS** use `await using ctx = testReactResource()` for TanStack React Query tests
+- Import `testReactResource` from `./__helpers` (not from other packages)
+- This provides TanStack-specific context creation and provider setup
+
+### Test Resource Management
+
+```typescript
+// ✅ CORRECT: Use await using for automatic cleanup
+await using ctx = testReactResource(appRouter, {
+  server: {
+    // server configuration
+  },
+  client(opts) {
+    return {
+      links: [
+        httpLink({
+          url: opts.httpUrl,
+          // client configuration
+        }),
+      ],
+    };
+  },
+});
+```
+
+### TanStack React Query Specific APIs
+
+- Use `ctx.useTRPC()` for the TanStack React Query hooks
+- Use `ctx.useTRPCClient()` for vanilla client access
+- Use `ctx.optionsProxyClient` for options proxy functionality
+- Use `ctx.optionsProxyServer` for server-side options proxy
+
+### Test Structure for TanStack React Query
+
+```typescript
+test('tanstack react query test', async () => {
+  await using ctx = testReactResource(appRouter);
+
+  function MyComponent() {
+    const query = ctx.useTRPC().post.byId.useQuery({ id: '1' });
+
+    return (
+      <div>
+        {query.data ? `Result: ${query.data}` : 'Loading...'}
+      </div>
+    );
+  }
+
+  const utils = ctx.renderApp(<MyComponent />);
+
+  await vi.waitFor(() => {
+    expect(utils.container).toHaveTextContent('Result:');
+  });
+});
+```
+
+### Provider Setup
+
+- Uses `TRPCProvider` from `createTRPCContext()`
+- Wraps with `QueryClientProvider` from `@tanstack/react-query`
+- Access via `ctx.renderApp()` and `ctx.rerenderApp()`
+
+### Testing Helper Context Pattern
+
+```typescript
+const testContext = () => {
+  const t = initTRPC.create({});
+
+  const appRouter = t.router({
+    // router definition
+  });
+
+  return {
+    ...testReactResource(appRouter),
+    // additional TanStack-specific utilities
+  };
+};
+```
+
+### Import Requirements for TanStack React Query
+
+#### Test Helper Imports
+
+- **ALWAYS** import `testReactResource` from `./__helpers` (local to tanstack-react-query package)
+- **NEVER** import from other packages' helpers - each package has its own implementation
+- Path: `import { testReactResource } from './__helpers';`
+
+#### Other Required Imports
+
+- Import `@testing-library/react` for rendering utilities
+- Import `@testing-library/user-event` for user interactions
+- Import React Query types from `@tanstack/react-query`
+- Import TanStack React Query utilities from `../src`
+- Import React testing utilities: `import * as React from 'react';`
+
+### Key Differences from Legacy React Query
+
+- Uses newer TanStack React Query provider pattern
+- Has `optionsProxyClient` and `optionsProxyServer` for options proxy testing
+- Uses `createTRPCContext()` instead of older React Query patterns
+- More streamlined context creation and provider setup
+
+### Helper Import Comparison
+
+```typescript
+// ✅ TanStack React Query (this package)
+import { testReactResource } from './__helpers';
+
+// ❌ DON'T use legacy React Query pattern
+import { createAppRouter } from './__testHelpers'; // Wrong package
+
+// ❌ DON'T use upgrade package pattern
+import { testReactResource } from './test/__helpers'; // Wrong path
+```
diff --git a/.cursor/rules/test-patterns.mdc b/.cursor/rules/test-patterns.mdc
@@ -0,0 +1,98 @@
+---
+description: tRPC testing patterns using testServerAndClientResource
+globs: ['**/*.test.ts']
+alwaysApply: false
+---
+
+# tRPC Testing Patterns
+
+## Server and Client Testing
+
+### ALWAYS use testServerAndClientResource
+
+- **ALWAYS** use `await using ctx = testServerAndClientResource()` for tests that need both server and client setup
+- **NEVER** use the deprecated `routerToServerAndClientNew()` function - it's marked as deprecated
+- Use the `testServerAndClientResource` import from `@trpc/client/__tests__/testClientResource`
+
+### Test Resource Management
+
+```typescript
+// ✅ CORRECT: Use await using for automatic cleanup
+await using ctx = testServerAndClientResource(router, {
+  client(opts) {
+    return {
+      links: [
+        httpLink({
+          url: opts.httpUrl,
+          fetch: mockFetch,
+        }),
+      ],
+    };
+  },
+});
+
+// ❌ INCORRECT: Don't use deprecated helper
+const { httpUrl, close } = routerToServerAndClientNew(router);
+// ... test code
+await close(); // Manual cleanup required
+```
+
+### Mock Setup
+
+- Create fresh mock instances per test using a factory function like `getMockFetch()`
+- Don't use global mocks that persist across tests
+- Configure mocks through the `client` callback in `testServerAndClientResource` options
+
+### Test Structure
+
+- Use the `ctx.client` directly from the test resource
+- Access server URLs via `ctx.httpUrl` and `ctx.wssUrl`
+- Configure server options via the `server` property in options
+- Configure client options via the `client` callback in options
+
+### Example Pattern
+
+```typescript
+test('my test', async () => {
+  const mockFetch = getMockFetch();
+  const t = initTRPC.create();
+
+  const router = t.router({
+    // router definition
+  });
+
+  await using ctx = testServerAndClientResource(router, {
+    server: {
+      // server configuration
+    },
+    client(opts) {
+      return {
+        links: [
+          httpLink({
+            url: opts.httpUrl,
+            fetch: mockFetch,
+            // other client options
+          }),
+        ],
+      };
+    },
+  });
+
+  // Use ctx.client for tests
+  const result = await ctx.client.myProcedure.query();
+
+  // Assert on mock calls
+  expect(mockFetch).toHaveBeenCalledTimes(1);
+});
+```
+
+### Test Naming
+
+- Use descriptive test names that explain the behavior being tested
+- Focus on what the test validates, not just what it does
+
+### Mock Best Practices
+
+- Use proper TypeScript typing for mocks
+- Clear mocks between tests when needed
+- Use factory functions for mock creation to ensure isolation
diff --git a/.cursor/rules/upgrade-tests.mdc b/.cursor/rules/upgrade-tests.mdc
@@ -0,0 +1,137 @@
+---
+description: tRPC Upgrade package testing patterns with dual provider support
+globs: ['packages/upgrade/**/*.test.tsx']
+alwaysApply: false
+---
+
+# tRPC Upgrade Package Testing Patterns
+
+## Upgrade Package Specific Testing
+
+### ALWAYS use testReactResource from local \_\_helpers
+
+- **ALWAYS** use `testReactResource()` from `./test/__helpers`
+- Supports both legacy React Query and TanStack React Query patterns
+- Provides dual provider setup for migration testing
+
+### Test Resource Management
+
+```typescript
+// ✅ CORRECT: Upgrade package pattern
+await using ctx = testReactResource(appRouter, {
+  server: {
+    // server configuration
+  },
+  client(opts) {
+    return {
+      links: [
+        httpLink({
+          url: opts.httpUrl,
+          // client configuration
+        }),
+      ],
+    };
+  },
+});
+```
+
+### Dual Provider Support
+
+- Has both `ctx.rq` (legacy React Query) and `ctx.trq` (TanStack React Query)
+- Supports testing component migrations between versions
+- Provides `optionsProxyClient` and `optionsProxyServer` for options testing
+
+### Test Structure for Upgrade Testing
+
+```typescript
+test('upgrade package test', async () => {
+  await using ctx = testReactResource(appRouter);
+
+  function MyComponent() {
+    // Can test both old and new patterns
+    const query = ctx.trq.useTRPC().post.byId.useQuery({ id: '1' });
+
+    return (
+      <div>
+        {query.data ? `Result: ${query.data}` : 'Loading...'}
+      </div>
+    );
+  }
+
+  const utils = ctx.renderApp(<MyComponent />);
+
+  await vi.waitFor(() => {
+    expect(utils.container).toHaveTextContent('Result:');
+  });
+});
+```
+
+### Provider Setup for Upgrade Package
+
+- Combines both legacy and modern provider patterns
+- Uses nested providers: `QueryClientProvider` > `baseProxy.Provider` > `TRPCProvider`
+- Includes `React.Suspense` wrapper for testing suspense behavior
+
+### Available APIs for Upgrade Testing
+
+- `ctx.rq` - Legacy React Query utilities (`createTRPCReact`)
+- `ctx.trq` - TanStack React Query utilities (`createTRPCContext`)
+- `ctx.optionsProxyClient` - Options proxy for client-side testing
+- `ctx.optionsProxyServer` - Options proxy for server-side testing
+
+### Migration Testing Pattern
+
+```typescript
+test('migration from legacy to modern', async () => {
+  await using ctx = testReactResource(appRouter);
+
+  // Test legacy component
+  function LegacyComponent() {
+    const baseProxy = ctx.rq as rq.CreateTRPCReactBase<typeof appRouter, unknown>;
+    // legacy pattern testing
+  }
+
+  // Test modern component
+  function ModernComponent() {
+    const query = ctx.trq.useTRPC().post.byId.useQuery({ id: '1' });
+    // modern pattern testing
+  }
+
+  // Both can be tested with same context
+});
+```
+
+### Import Requirements for Upgrade Package
+
+#### Test Helper Imports
+
+- **ALWAYS** import `testReactResource` from `./test/__helpers` (note the `test/` prefix)
+- **UNIQUE**: Upgrade package has different path structure than other packages
+- Path: `import { testReactResource } from './test/__helpers';` (from package root)
+- Alternative path from test files: `import { testReactResource } from './__helpers';`
+
+#### Dual Package Imports for Migration Testing
+
+- Import both legacy and modern patterns:
+  - `import * as rq from '@trpc/react-query'` (legacy)
+  - `import * as trq from '@trpc/tanstack-react-query'` (modern)
+- Import `@testing-library/react` for rendering
+- Import testing utilities for component transformation testing
+
+### Fixture Testing Support
+
+- Supports `.tsx`, `.snap.tsx`, `.trpc.tsx`, and `.spec.tsx` file patterns
+- Can test component transformations and upgrades
+- Provides utilities for testing codemod transformations
+
+### Helper Import Comparison
+
+```typescript
+// ✅ Upgrade Package (this package)
+import { testReactResource } from './__helpers';     // From test files
+import { testReactResource } from './test/__helpers'; // From package root
+
+// ❌ DON'T use other package patterns
+import { createAppRouter } from './__testHelpers';    // Legacy React Query only
+import { testReactResource } from './__helpers';      // TanStack only (different impl)
+```
PATCH

echo "Gold patch applied."
