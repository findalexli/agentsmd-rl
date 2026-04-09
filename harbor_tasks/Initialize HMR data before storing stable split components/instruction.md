# Fix HMR Data Initialization in Router Plugin

## Problem

When running code with Vitest that uses TanStack Router's code-splitting plugin, the application crashes with an error about accessing a property on `undefined`. This happens because `import.meta.hot.data` can be `undefined` when HMR (Hot Module Replacement) is not fully initialized, but the code attempts to access it directly.

## Your Task

Fix the crash in the router-plugin's HMR handling for stable split route components.

## Details

The issue is in the `@tanstack/router-plugin` package. When the plugin generates code for stable split components with HMR enabled, it produces code like:

```javascript
if (import.meta.hot) {
  import.meta.hot.data["tsr-split-component:component"] = TSRSplitComponent
}
```

This crashes when `import.meta.hot.data` is `undefined` (which occurs in Vitest test environments without full HMR setup).

## Files to Modify

- `packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts`

The fix involves ensuring `import.meta.hot.data` is initialized before being accessed. JavaScript's nullish coalescing assignment operator (`??=`) is the idiomatic way to handle this.

## Expected Behavior After Fix

The generated code should initialize `import.meta.hot.data` before storing components:

```javascript
if (import.meta.hot) {
  import.meta.hot.data ??= {}
  import.meta.hot.data["tsr-split-component:component"] = TSRSplitComponent
}
```

## Hints

- Look at the `buildStableSplitComponentStatements` template in the source file
- The template uses Babel's `template.statements` with syntactic placeholders
- You only need to add a single line to initialize the data object
- Run the unit tests in `packages/router-plugin/tests/add-hmr.test.ts` to verify your fix

## Testing

After making the fix:
1. Build the package: `pnpm nx run @tanstack/router-plugin:build`
2. Run the HMR tests: `pnpm nx run @tanstack/router-plugin:test:unit -- tests/add-hmr.test.ts`
3. The new regression test `initializes import.meta.hot.data before storing stable split components` should pass
