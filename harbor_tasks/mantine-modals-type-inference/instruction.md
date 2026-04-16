# Simplify MantineModals Type in @mantine/modals

## Problem

The `MantineModals` type exported from `packages/@mantine/modals/src/context.ts` is implemented with unnecessary verbosity. Near the end of that file, the code uses a two-step pattern: first a conditional type wraps `MantineModalsOverride`, then a separate type indexes into the result with `['modals']`. This indirection makes the code harder to read than it needs to be.

## Expected Result

The `MantineModals` type should be a single self-contained conditional type definition — no intermediate helper types for it should remain in the file. Specifically, after simplification the file must contain exactly:

```
export type MantineModals = MantineModalsOverride extends { modals: infer M }
  ? M
  : Record<string, React.FC<ContextModalProps<any>>>;
```

## Constraints

- Do not modify the `MantineModalsOverride` interface or the `MantineModal` type definition
- The public API types must remain backward compatible
- All tooling checks must pass from the repo root (`/workspace/mantine`):
  - TypeScript: `yarn tsc --noEmit`
  - Tests: `yarn jest packages/@mantine/modals/src/use-modals/use-modals.test.tsx`
  - Lint: `yarn eslint packages/@mantine/modals --cache`
  - Format: `yarn prettier --check 'packages/@mantine/modals/src/**/*.{ts,tsx}'`
