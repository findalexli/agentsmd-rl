# Fix TypeScript Type Safety Issues in Test Utilities

The ant-design test utilities have type safety issues that reduce TypeScript's ability to catch bugs at compile time. Unsafe use of `any` types, missing type parameters on generic functions, and lack of proper null checking force the code to rely on type assertions that bypass TypeScript's type checker.

## Affected Files

1. **`tests/setupAfterEnv.ts`** - Snapshot serialization utilities
2. **`tests/shared/focusTest.tsx`** - Focus testing utilities for components
3. **`package.json`** - Dependency configuration for resolving version conflicts

## Problem Description

### In tests/setupAfterEnv.ts:

The `formatHTML` function handles multiple DOM element types (single `HTMLElement`, `DocumentFragment`, `HTMLCollection`, `NodeList`, arrays of `Node`), but currently uses `any` types that disable TypeScript's compile-time checking. This causes:

1. Type errors when the function is called with properly-typed elements
2. Need for unsafe `as any` type assertions in the snapshot serializers
3. Internal `cloneNodes` variable lacks proper typing

To fix this, you need to:

- Define a `SnapshotTarget` union type that covers all valid DOM element types the function accepts
- Replace the `any` parameter type on `formatHTML` with this new type
- Properly type the internal `cloneNodes` variable (hint: it's used with `Array.from()` and `.map()`)
- Replace `as any` assertions with appropriate specific type assertions where needed
- Update the `print` callbacks in snapshot serializers to use proper type assertions

### In tests/shared/focusTest.tsx:

The focus testing utilities use refs for focusable elements without proper type parameters, causing the refs to default to `any`. This results in:

1. TypeScript errors when calling `ref.current.focus()` or `ref.current.blur()`
2. Need for non-null assertion operators (`!`) on `getElement()` results
3. Missing generic type parameters on `querySelector` calls

To fix this, you need to:

- Define a `FocusableRef` type with `focus()` and `blur()` methods (both returning void)
- Replace `React.createRef<any>()` with properly typed refs using the new type
- Add an explicit return type annotation to the `getElement` helper function
- Add generic type parameters to `querySelector` calls to specify the return type
- Add a null check assertion before returning from `getElement` (so callers don't need `!`)
- After these changes, `fireEvent` calls should work without non-null assertions on getElement

### In package.json:

After making the type changes, TypeScript compilation may fail due to dependency version conflicts with `@sinonjs/fake-timers`. You must resolve this by pinning `@sinonjs/fake-timers` to version `15.2.0` using the appropriate configuration fields for pnpm, npm, and yarn (usually `pnpm.overrides`, `overrides`, and `resolutions`).

## Verification

After your changes:
- `npx tsc --noEmit` should pass without type errors
- `npx eslint tests/setupAfterEnv.ts tests/shared/focusTest.tsx` should not report @typescript-eslint/no-explicit-any errors
- `npm run lint` should pass successfully

## References

- The repository uses strict TypeScript checking
- See `.github/copilot-instructions.md` for TypeScript coding standards
- Check existing component implementations for ref typing patterns
