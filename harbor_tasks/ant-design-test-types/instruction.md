# Fix TypeScript Type Safety in Test Utilities

The ant-design test utilities have reduced type safety due to use of `any` types. This causes TypeScript to lose type information and prevents catching potential bugs at compile time.

## Affected Files

1. **`tests/setupAfterEnv.ts`** - Snapshot serialization utilities
2. **`tests/shared/focusTest.tsx`** - Focus testing utilities for components

## What's Wrong

### In tests/setupAfterEnv.ts:
- The `formatHTML` function uses `any` type for its parameter and local variables
- Type assertions use `as any` instead of proper types
- The `print` callback functions don't properly type their elements

### In tests/shared/focusTest.tsx:
- `React.createRef<any>()` is used instead of a proper ref type
- The `getElement` function lacks return type annotation
- `querySelector` calls don't use generic type parameters
- `fireEvent` calls use the non-null assertion operator `!` because the element type is nullable
- The `FocusableRef` type is not defined (should describe refs with focus/blur methods)

## Your Task

Improve type safety in both files by:

1. **In tests/setupAfterEnv.ts:**
   - Define a `SnapshotTarget` type for DOM elements (union of HTMLElement, DocumentFragment, HTMLCollection, NodeList, Node[])
   - Update `formatHTML` to use `SnapshotTarget` instead of `any`
   - Replace `as any` with `as HTMLElement` in cloneNode calls
   - Add proper type assertions where elements are passed to `formatHTML`

2. **In tests/shared/focusTest.tsx:**
   - Define a `FocusableRef` type with `focus: () => void` and `blur: () => void` methods
   - Replace `React.createRef<any>()` with `React.createRef<FocusableRef>()`
   - Update `getElement` to return `HTMLElement` and add null check assertion
   - Use `querySelector<HTMLElement>()` for type-safe element selection
   - Remove the `!` non-null assertion from `fireEvent` calls (getElement now returns non-null HTMLElement)

## Verification

After your changes:
- `npx tsc --noEmit` should pass without type errors
- `npx eslint tests/setupAfterEnv.ts tests/shared/focusTest.tsx` should not report @typescript-eslint/no-explicit-any errors

## References

- The repository uses strict TypeScript checking
- See `.github/copilot-instructions.md` for TypeScript coding standards
- Check existing component implementations for ref typing patterns
