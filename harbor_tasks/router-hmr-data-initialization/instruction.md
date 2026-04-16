# Fix HMR Data Initialization in Stable Split Route Components

## Problem

When using Hot Module Replacement (HMR) with stable split route components in Vitest, the router plugin crashes at runtime. The generated code attempts to set properties on `import.meta.hot.data` without first ensuring that object exists.

The symptom is a runtime error: `Cannot set properties of undefined (setting '...')` when Vitest runs tests with HMR enabled.

## Context

The issue occurs in the router-plugin package. The code generation template for HMR-aware components produces code that reads HMR data, but when writing back it does not handle the case where the HMR data object is uninitialized.

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

## Requirements

1. The router-plugin package must build successfully without type errors
2. All existing router-plugin unit tests must continue to pass
3. The generated code for HMR-enabled routes must handle the case where `import.meta.hot.data` is undefined before properties are written to it

## File Under Test

`packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts`

This file contains the `buildStableSplitComponentStatements` template. The template generates code that reads from and writes to HMR data using keys like `%%hotDataKey%%`.