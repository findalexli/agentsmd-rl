# Fix HMR Data Initialization in Stable Split Route Components

## Problem

When using Hot Module Replacement (HMR) with stable split route components in Vitest, the router plugin crashes because it attempts to store data on `import.meta.hot.data` before ensuring the object is initialized.

The code transformation in the router-plugin generates code that directly accesses `import.meta.hot.data[key]` without first checking if `import.meta.hot.data` exists. When Vitest runs tests with HMR enabled but without prior HMR state, this causes a runtime error.

## Location

The relevant file is:
- `packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts`

This file contains a Babel template that generates the HMR-aware code for stable split components. Look for the `buildStableSplitComponentStatements` template.

## Expected Behavior

The generated code should initialize `import.meta.hot.data` to an empty object before attempting to store values on it. The pattern should be:

1. Check if there's an existing component in `import.meta.hot.data[key]`
2. If not, create a new one
3. **Initialize `import.meta.hot.data` if it doesn't exist** (this is the missing step)
4. Store the component reference for future HMR cycles

## Reproduction

The bug manifests when:
1. Code splitting with HMR is enabled (`addHmr: true`)
2. A route component is being compiled
3. The compiled output is executed in an environment where `import.meta.hot.data` is undefined

Run the router-plugin unit tests to see the expected behavior and test the fix.

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

The fix requires modifying the Babel template in `react-stable-hmr-split-route-components.ts` to add initialization of `import.meta.hot.data` before storing to it.
