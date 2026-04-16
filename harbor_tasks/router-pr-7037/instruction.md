# TypeScript TS4023 Error When Wrapping useBlocker

## Problem

Users are reporting a TypeScript error (TS4023) when they try to wrap the `useBlocker` hook from `@tanstack/react-router` in a custom hook and export it from their module.

The error message looks like:
```
error TS4023: Exported variable 'useCustomBlocker' has or is using name 'ShouldBlockFnLocation' from external module "/path/to/node_modules/@tanstack/react-router/dist/esm/useBlocker" but cannot be named.
```

This happens when users create patterns like:

```typescript
import { useBlocker } from '@tanstack/react-router';

export function useCustomBlocker(shouldBlock: boolean) {
    return useBlocker({
        shouldBlockFn: () => shouldBlock,
    });
}
```

The error only appears when TypeScript generates declaration files (`.d.ts`), which is common in library code or when using `declaration: true` in tsconfig.

## Affected Files

The issue originates in the `useBlocker.tsx` files across the router packages:
- `packages/react-router/src/useBlocker.tsx`
- `packages/solid-router/src/useBlocker.tsx`
- `packages/vue-router/src/useBlocker.tsx`

## Expected Behavior

Users should be able to wrap `useBlocker` in custom hooks and export them without TypeScript errors.

## Additional Context

- The issue is related to how TypeScript handles type declarations that reference internal types
- The fix should be consistent across all router packages (React, Solid, Vue)
- Documentation in `docs/router/api/router/useBlockerHook.md` should reflect any API changes
