# Task: Fix TS4023 Error - Convert ShouldBlockFnLocation from Interface to Type

## Problem

When `useBlocker` is wrapped in a custom hook and the blocker is returned, TypeScript throws error TS4023: "'ShouldBlockFnLocation' cannot be named".

This happens because `ShouldBlockFnLocation` is declared as an unexported `interface` in the router packages. When a public API returns a type that references this unexported interface, TypeScript cannot write the type declaration file.

## Files to Modify

The same fix needs to be applied in three files:

1. `packages/react-router/src/useBlocker.tsx`
2. `packages/solid-router/src/useBlocker.tsx`
3. `packages/vue-router/src/useBlocker.tsx`

## What to Fix

In each file, find the `ShouldBlockFnLocation` declaration (currently an `interface`) and convert it to a `type` alias.

Current (problematic):
```typescript
interface ShouldBlockFnLocation<
  out TRouteId,
  out TFullPath,
  out TAllParams,
  out TFullSearchSchema,
> {
  routeId: TRouteId
  // ... other properties
}
```

Expected (fixed):
```typescript
type ShouldBlockFnLocation<
  out TRouteId,
  out TFullPath,
  out TAllParams,
  out TFullSearchSchema,
> = {
  routeId: TRouteId
  // ... other properties
}
```

## Verification

- TypeScript type checking should pass for all three packages
- The TS4023 error should no longer occur when wrapping `useBlocker` in a custom hook

## Testing Commands

Run the type checkers for each package:
```bash
pnpm nx run @tanstack/react-router:test:types
pnpm nx run @tanstack/solid-router:test:types
pnpm nx run @tanstack/vue-router:test:types
```
