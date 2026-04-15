# Fix HMR Data Initialization in Stable Split Route Components

## Problem

When using Hot Module Replacement (HMR) with stable split route components in Vitest, the router plugin crashes at runtime because the generated code accesses `import.meta.hot.data` properties without ensuring the object is initialized first.

The symptom is a runtime error when Vitest runs tests with HMR enabled but without prior HMR state. The generated code should gracefully handle the case where `import.meta.hot.data` is undefined.

## What the Tests Check

The test file `packages/router-plugin/tests/add-hmr.test.ts` validates the generated code structure.

The source file at `packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts` contains a Babel template (`buildStableSplitComponentStatements`) that generates HMR-aware code for stable split components.

**Required patterns in the source code template:**

1. The template reads from `import.meta.hot?.data?.[%%hotDataKey%%]` with optional chaining
2. The template writes to `import.meta.hot.data[%%hotDataKey%%]`
3. Before writing to `import.meta.hot.data[key]`, the `import.meta.hot.data` object must be initialized

The tests verify these exact string patterns exist in the source file (as Babel template syntax with `%%hotDataKey%%` placeholders) and that any initialization comes before the data access.

## Reproduction

The bug manifests when:
1. Code splitting with HMR is enabled (`addHmr: true`)
2. A route component is being compiled
3. The compiled output is executed in an environment where `import.meta.hot.data` is undefined

## Agent Instructions

This is a pnpm monorepo using Nx for task orchestration. Use these commands:

```bash
# Install dependencies
pnpm install

# Build the router-plugin package
CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-plugin:build --outputStyle=stream --skipRemoteCache

# Run router-plugin tests
CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-plugin:test:unit --outputStyle=stream --skipRemoteCache
```
