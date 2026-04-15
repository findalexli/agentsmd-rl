# Fix HMR Data Initialization in Stable Split Route Components

## Problem

When using Hot Module Replacement (HMR) with stable split route components in Vitest, the router plugin crashes at runtime. The generated code attempts to set properties on `import.meta.hot.data` without first ensuring that object exists.

The symptom is a runtime error: `Cannot set properties of undefined (setting '...')` when Vitest runs tests with HMR enabled. This occurs because the generated code writes to `import.meta.hot.data[key]` but `import.meta.hot.data` may be undefined during initial execution.

## Context

The issue occurs in the router-plugin package which generates code for stable split route components. The code generation template for HMR-aware components produces output that:
1. Reads from `import.meta.hot?.data?.[key]` using optional chaining to retrieve cached component references
2. Writes to `import.meta.hot.data[key]` to store component references for HMR preservation

The problem is that the write operation assumes `import.meta.hot.data` exists, but in Vitest with HMR enabled, this object starts as undefined.

## Reproduction

The bug manifests when:
1. Code splitting with HMR is enabled (`addHmr: true`)
2. A route component is being compiled
3. The compiled output is executed in an environment where `import.meta.hot.data` is undefined

The generated code must gracefully handle the case where `import.meta.hot.data` is undefined before attempting to write properties to it.

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
3. The generated code for HMR-enabled routes must handle the case where `import.meta.hot.data` is undefined
4. The fix should apply to the code generation template that creates HMR-aware component statements
