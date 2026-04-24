# HMR Crash in Vitest with Split Route Components

## Problem

When using TanStack Router's code-splitting feature with Vitest, the application crashes during hot module replacement (HMR). The error occurs because in Vitest's HMR environment, `import.meta.hot` exists but `import.meta.hot.data` is `undefined` (not pre-initialized), causing a crash when code attempts to store stable split component references for HMR persistence.

## Symptoms

- Vitest crashes when running tests that use code-split routes with HMR enabled
- Error message: `TypeError: Cannot set properties of undefined (setting 'tsr-split-component:component')`
- The issue does not occur in regular Vite development mode where `import.meta.hot.data` is pre-initialized

## Technical Context

The crash occurs in generated code produced by the router-plugin package. When the plugin processes code-split routes, it generates HMR persistence code using Babel's `template.statements`. The generated code follows this pattern:

```javascript
const TSRSplitComponent = import.meta.hot?.data?.["tsr-split-component:component"] ?? lazyRouteComponent(importer, "component")
if (import.meta.hot) {
  import.meta.hot.data["tsr-split-component:component"] = TSRSplitComponent
}
```

The problem is that this code directly assigns to `import.meta.hot.data[key]` without first ensuring `import.meta.hot.data` is initialized. In Vitest's HMR environment, `import.meta.hot` exists but `import.meta.hot.data` is `undefined`, causing the assignment to fail.

## Required Behavior

The code generator that produces HMR persistence code must be modified to ensure `import.meta.hot.data` is initialized to an empty object `{}` before any assignments are made to it. The initialization must:

1. Use the nullish coalescing assignment operator (`??=`) to set `import.meta.hot.data` to `{}` only if it is `undefined` or `null`
2. Occur inside the `if (import.meta.hot)` block, before any `import.meta.hot.data[key] = value` assignments

## Generated Code Structure

The fixed template should produce code structured like this:

```javascript
if (import.meta.hot) {
  import.meta.hot.data ??= {}
  import.meta.hot.data["some-key"] = someValue
}
```

## Files to Modify

The code generation template is located in the router-plugin package at:

```
packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts
```

Look for the Babel template that generates the HMR persistence statements.

## Verification

After making changes, run the router-plugin test suite to verify:

```bash
pnpm nx run @tanstack/router-plugin:test:unit
```

All tests should pass, including any tests related to HMR code generation.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
