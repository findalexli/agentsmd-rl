# React HMR Not Working for Inline Route Components

## Problem

When using TanStack Router with file-based routing, React's Hot Module Replacement (HMR) does not work properly for routes that define their component as an inline arrow function or function expression.

For example, this route definition fails to hot-reload:

```tsx
export const Route = createRootRoute({
  component: () => <div>Hello World</div>,
})
```

React Refresh cannot track anonymous inline functions for HMR updates. The component needs to be defined as a named module-level declaration for React Refresh to register it.

## Expected Behavior

When HMR is enabled, inline component definitions should be automatically hoisted to module-level named declarations during compilation. For example, the above should be transformed to:

```tsx
const TSRComponent = () => <div>Hello World</div>;
export const Route = createRootRoute({
  component: TSRComponent
})
```

## Required API Surface

The fix must be implemented within the `packages/router-plugin` package. After the fix, the following elements must be present in the codebase:

### Unique Identifier Utility

A function named `getUniqueProgramIdentifier` must be exported from `packages/router-plugin/src/core/utils.ts`. It must:
- Accept parameters named `programPath` and `baseName`
- Use a `suffix` counter that increments in a `while` loop until a unique name is found
- Check for existing bindings using `hasBinding` and/or `hasGlobal`

### Plugin Type Definitions

A file at `packages/router-plugin/src/core/code-splitter/plugins.ts` must exist and define:
- A type named `ReferenceRouteCompilerPlugin`
- A type named `ReferenceRouteCompilerPluginContext`
- An `onUnsplittableRoute` hook in the plugin interface

### React Refresh Component Plugin

A file at `packages/router-plugin/src/core/code-splitter/plugins/react-refresh-route-components.ts` must exist and:
- Export a function named `createReactRefreshRouteComponentsPlugin`
- Handle all four route option identifiers: `component`, `pendingComponent`, `errorComponent`, `notFoundComponent`
- Create hoisted variable declarations (the code must contain `hoistedDeclarations` and/or `variableDeclaration`)
- Use `getUniqueProgramIdentifier` for collision-free naming

### Framework Plugin Factory

A file at `packages/router-plugin/src/core/code-splitter/plugins/framework-plugins.ts` must exist and:
- Export a function named `getReferenceRouteCompilerPlugins`
- Handle the `react` target framework case
- Return `createReactRefreshRouteComponentsPlugin` for React

### Integration with Existing Compilation Pipeline

The following existing files must be updated to integrate the plugin system:

- `packages/router-plugin/src/core/code-splitter/compilers.ts`: Must accept a `compilerPlugins` option in `compileCodeSplitReferenceRoute` and reference the `ReferenceRouteCompilerPlugin` type
- `packages/router-plugin/src/core/router-code-splitter-plugin.ts`: Must use `getReferenceRouteCompilerPlugins` and pass `compilerPlugins` to the compiler
- `packages/router-plugin/src/core/router-hmr-plugin.ts`: Must use `getReferenceRouteCompilerPlugins` and call `compileCodeSplitReferenceRoute` for the React target framework

## Behavioral Requirements

The transformation should:
1. Apply to `component`, `pendingComponent`, `errorComponent`, and `notFoundComponent` route options
2. Generate unique identifier names that don't collide with existing bindings in the program scope
3. Only apply when HMR is enabled and the target framework is React

## Quality Requirements

The existing ESLint, build, build validation, unit tests, and type checks in the `@tanstack/router-plugin` package must continue to pass.
