# Task: Fix TS4023 Error in useBlocker API

## Problem

When `useBlocker` is wrapped in a custom hook that returns the blocker with `withResolver: true`, TypeScript throws error TS4023: "'ShouldBlockFnLocation' cannot be named".

This occurs because the `ShouldBlockFnLocation` type used by the `useBlocker` hook is referenced by the return type but cannot be named in type declaration files.

## Files Affected

The following files contain the `ShouldBlockFnLocation` declaration:

- `packages/react-router/src/useBlocker.tsx`
- `packages/solid-router/src/useBlocker.tsx`
- `packages/vue-router/src/useBlocker.tsx`

## Requirements

1. Fix the TS4023 error so that wrapping `useBlocker` in a custom hook with `withResolver: true` compiles without errors
2. TypeScript type checking must continue to pass for all router packages
3. All existing unit tests must continue to pass
4. ESLint, publint, and attw checks must continue to pass

## TypeScript Error Reference

- Error code: TS4023
- Error message: "'ShouldBlockFnLocation' cannot be named"
- Trigger: Returning `useBlocker` result from a custom hook with `withResolver: true`

## Verification Commands

After fixing, these commands should all pass:

```bash
pnpm nx run @tanstack/react-router:test:types
pnpm nx run @tanstack/solid-router:test:types
pnpm nx run @tanstack/vue-router:test:types
```

## Testing Commands

To verify the TS4023 regression is fixed, create a test file that wraps `useBlocker`:

```typescript
import { useBlocker } from './useBlocker'

export const useCustomBlocker = () => {
  const blocker = useBlocker({ shouldBlockFn: () => true, withResolver: true })
  return { blocker }
}
```

Compile with `tsc --noEmit` to verify no TS4023 error is produced.
