# Fix TypeScript Type Safety Issues in Test Utilities

The ant-design test utilities have type safety issues that reduce TypeScript's ability to catch bugs at compile time. These issues manifest as `any` types being used where more specific types would provide better type checking.

## Affected Files

1. **`tests/setupAfterEnv.ts`** - Snapshot serialization utilities
2. **`tests/shared/focusTest.tsx`** - Focus testing utilities for components
3. **`package.json`** - Dependency configuration

## What's Wrong

### In tests/setupAfterEnv.ts:
The snapshot serialization code lacks proper TypeScript typing:
- The `formatHTML` function accepts DOM elements but lacks proper type annotations for its parameters
- Variables holding cloned nodes use `any` type instead of more specific types
- Type assertions in the code use `as any` which bypasses type checking
- The `print` callback functions pass elements to `formatHTML` without proper type assertions

### In tests/shared/focusTest.tsx:
The focus testing utilities have several type safety gaps:
- `React.createRef()` is called without a type parameter for refs that have `focus()` and `blur()` methods
- The `getElement` function lacks return type annotation and performs unchecked nullable lookups
- `querySelector` calls don't use generic type parameters for element selection
- `fireEvent` calls rely on the non-null assertion operator `!` because element types are nullable

### In package.json:
After making the above type changes, TypeScript compilation may fail due to dependency version conflicts with `@sinonjs/fake-timers`. The package.json needs configuration adjustments (pnpm overrides, npm overrides, or resolutions) to resolve these conflicts by pinning `@sinonjs/fake-timers` to version `15.2.0`.

## Your Task

Improve type safety in both test utility files by addressing the symptoms described above.

Specific requirements the tests verify:

1. **In tests/setupAfterEnv.ts:**
   - A `SnapshotTarget` type must be defined that represents the union of: `HTMLElement`, `DocumentFragment`, `HTMLCollection`, `NodeList`, and `Node[]`
   - The `formatHTML` function must use this `SnapshotTarget` type for its `nodes` parameter
   - The `cloneNodes` variable must be typed as `Node | Node[]`
   - All `as any` assertions must be replaced with proper type assertions
   - Both `print` callback functions must cast their elements to `SnapshotTarget` when calling `formatHTML`

2. **In tests/shared/focusTest.tsx:**
   - A `FocusableRef` type must be defined with `focus: () => void` and `blur: () => void` methods
   - `React.createRef<FocusableRef>()` must be used instead of `React.createRef<any>()`
   - The `getElement` function must have an explicit return type of `HTMLElement`
   - All `querySelector` calls must use the generic form: `querySelector<HTMLElement>()`
   - An `expect(element).not.toBeNull()` assertion must be added before returning the element
   - All non-null assertion operators (`!`) on `getElement(container)` calls must be removed

3. **In package.json:**
   - Configuration for `@sinonjs/fake-timers` version `15.2.0` must be added via `pnpm.overrides`, `overrides`, and `resolutions` fields

## Verification

After your changes:
- `npx tsc --noEmit` should pass without type errors
- `npx eslint tests/setupAfterEnv.ts tests/shared/focusTest.tsx` should not report @typescript-eslint/no-explicit-any errors
- `npm run lint` should pass successfully

## References

- The repository uses strict TypeScript checking
- See `.github/copilot-instructions.md` for TypeScript coding standards
- Check existing component implementations for ref typing patterns
