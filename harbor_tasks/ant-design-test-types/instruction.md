# Fix TypeScript Type Safety Issues in Test Utilities

The ant-design test utilities have type safety issues that reduce TypeScript's ability to catch bugs at compile time. Unsafe use of `any` types, missing type parameters on generic functions, and lack of proper null checking force the code to rely on type assertions that bypass TypeScript's type checker.

## Affected Files

1. **`tests/setupAfterEnv.ts`** - Snapshot serialization utilities
2. **`tests/shared/focusTest.tsx`** - Focus testing utilities for components
3. **`package.json`** - Dependency configuration

## Required Type Definitions

The following specific type definitions, function signatures, and strings must be present in the codebase after your changes:

### In tests/setupAfterEnv.ts:

1. A type named **`SnapshotTarget`** defined as:
   ```typescript
type SnapshotTarget = HTMLElement | DocumentFragment | HTMLCollection | NodeList | Node[]
```

2. The **`formatHTML`** function must use `SnapshotTarget` as its parameter type:
   ```typescript
function formatHTML(nodes: SnapshotTarget)
```

3. The **`cloneNodes`** variable must be typed as:
   ```typescript
let cloneNodes: Node | Node[]
```

4. The code must NOT use `as any` for type assertions; use **`as HTMLElement`** or **`as SnapshotTarget`** instead

5. Both **`print`** callback functions in the snapshot serializers must pass elements to `formatHTML` with the type assertion **`as SnapshotTarget`** (at least 2 occurrences required)

### In tests/shared/focusTest.tsx:

1. A type named **`FocusableRef`** with this exact structure:
   ```typescript
type FocusableRef = {
  focus: () => void;
  blur: () => void;
};
```

2. **`React.createRef()`** must be called with the type parameter **`FocusableRef`**:
   ```typescript
React.createRef<FocusableRef>()
```
   It must NOT use `React.createRef<any>()`

3. The **`getElement`** function must have this exact signature with explicit return type:
   ```typescript
const getElement = (container: HTMLElement): HTMLElement => {
```

4. All **`querySelector`** calls must use the generic type parameter **`HTMLElement`**:
   ```typescript
querySelector<HTMLElement>(...)
```

5. The **`getElement`** function must include a null check assertion using **`expect(element).not.toBeNull()`** before returning the element

6. All **`fireEvent`** calls (e.g., `fireEvent.focus()`, `fireEvent.blur()`) must NOT use the non-null assertion operator (`!`) on `getElement(container)` calls. The pattern **`getElement(container)!`** must NOT appear in the file.

### In package.json:

The package.json must include version **`15.2.0`** for **`@sinonjs/fake-timers`** configured via all three of the following fields:
- **`pnpm.overrides`**
- **`overrides`** (npm)
- **`resolutions`** (yarn)

## Problem Description

The snapshot serialization code in `tests/setupAfterEnv.ts` handles multiple DOM element types including single `HTMLElement`, `DocumentFragment`, `HTMLCollection`, `NodeList`, and arrays of `Node` elements, but currently uses implicit `any` types that disable TypeScript's compile-time checking. The lack of a proper union type for the `formatHTML` parameter means type errors at call sites are not caught.

The focus testing utilities in `tests/shared/focusTest.tsx` use refs for focusable elements without proper type parameters, causing the refs to default to `any`. The `querySelector` calls don't use generic type parameters to specify the return type, and the `getElement` function lacks proper return type annotations and null checking, forcing callers to use unsafe non-null assertions with the `!` operator.

After making the type changes, TypeScript compilation may fail due to dependency version conflicts with `@sinonjs/fake-timers`, which must be resolved by pinning to version `15.2.0`.

## Verification

After your changes:
- `npx tsc --noEmit` should pass without type errors
- `npx eslint tests/setupAfterEnv.ts tests/shared/focusTest.tsx` should not report @typescript-eslint/no-explicit-any errors
- `npm run lint` should pass successfully

## References

- The repository uses strict TypeScript checking
- See `.github/copilot-instructions.md` for TypeScript coding standards
- Check existing component implementations for ref typing patterns
