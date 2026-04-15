# Fix TypeScript Type Safety Issues in Test Utilities

The ant-design test utilities have type safety issues that reduce TypeScript's ability to catch bugs at compile time. These issues manifest as `any` types being used where more specific types would provide better type checking.

## Affected Files

1. **`tests/setupAfterEnv.ts`** - Snapshot serialization utilities
2. **`tests/shared/focusTest.tsx`** - Focus testing utilities for components
3. **`package.json`** - Dependency configuration

## What's Wrong

### In tests/setupAfterEnv.ts:
The snapshot serialization code lacks proper TypeScript typing:
- The `formatHTML` function accepts DOM elements but lacks proper type annotations for its parameters (currently uses `any`)
- Variables holding cloned nodes use `any` type instead of more specific DOM types
- Type assertions in the code use `as any` which bypasses type checking; these should use proper HTMLElement assertions
- The `print` callback functions pass elements to `formatHTML` without proper type assertions that match the expected parameter types

The `formatHTML` function handles multiple DOM element types: single `HTMLElement`, `DocumentFragment`, `HTMLCollection`, `NodeList`, and arrays of `Node` elements. It needs a proper type that represents this union of possible inputs.

### In tests/shared/focusTest.tsx:
The focus testing utilities have several type safety gaps:
- `React.createRef()` is called without a type parameter for refs that have `focus()` and `blur()` methods, falling back to `any`
- The `getElement` function lacks return type annotation and performs unchecked nullable lookups
- `querySelector` calls don't use generic type parameters for element selection
- `fireEvent` calls rely on the non-null assertion operator `!` because `getElement` returns a nullable type; once properly typed, these assertions should be removable

The `getElement` function searches for focusable elements (input, button, textarea, or div with tabIndex) but doesn't guarantee a return value, forcing callers to use unsafe non-null assertions.

### In package.json:
After making the above type changes, TypeScript compilation may fail due to dependency version conflicts with `@sinonjs/fake-timers`. The package.json needs configuration adjustments (pnpm.overrides, npm overrides, or resolutions) to resolve these conflicts by pinning `@sinonjs/fake-timers` to version `15.2.0`.

## What Needs to Be Fixed

Your task is to:

1. **In tests/setupAfterEnv.ts:**
   - Define a type that represents all valid snapshot targets (HTMLElement, DocumentFragment, HTMLCollection, NodeList, and arrays of Node elements)
   - Update `formatHTML` to use this type for its parameter
   - Add proper type annotations to the `cloneNodes` variable
   - Replace unsafe `as any` assertions with proper `as HTMLElement` assertions
   - Update both `print` callback functions to properly assert elements before passing to `formatHTML`

2. **In tests/shared/focusTest.tsx:**
   - Define a type for focusable refs that includes `focus()` and `blur()` methods
   - Use properly typed `React.createRef()` with the focusable ref type
   - Update `getElement` to have an explicit return type and include a null check assertion before returning
   - Use generic type parameters for all `querySelector` calls
   - Remove all non-null assertion operators (`!`) on `getElement(container)` calls for `fireEvent` operations

3. **In package.json:**
   - Add configuration for `@sinonjs/fake-timers` version `15.2.0` via `pnpm.overrides`, `overrides`, and `resolutions` fields

## Verification

After your changes:
- `npx tsc --noEmit` should pass without type errors
- `npx eslint tests/setupAfterEnv.ts tests/shared/focusTest.tsx` should not report @typescript-eslint/no-explicit-any errors
- `npm run lint` should pass successfully

## References

- The repository uses strict TypeScript checking
- See `.github/copilot-instructions.md` for TypeScript coding standards
- Check existing component implementations for ref typing patterns
