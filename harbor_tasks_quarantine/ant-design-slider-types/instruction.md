# Fix Slider TypeScript Type Errors

The Ant Design Slider component in `components/slider/index.tsx` has TypeScript type issues that prevent strict type checking.

## Problem

The file contains three type-related issues that must be fixed for the codebase to pass `npx tsc --noEmit`:

1. A `// @ts-ignore` comment suppressing type errors on the RcSlider component. Type suppression comments should not be needed — the underlying type mismatch should be fixed instead.

2. In the `onInternalChangeComplete` callback, `onChangeComplete?.(nextValues)` uses `as any` on the `nextValues` argument to suppress a type error. This creates unsafe typing that bypasses TypeScript's checks. The fix should eliminate the `as any` pattern while ensuring the code compiles without errors.

3. The `restProps` object is spread onto the RcSlider component without type narrowing. The `restProps` includes `onAfterChange` and `onChange` properties that conflict with the component's internal handling of these callbacks, which causes the type error suppressed by the `// @ts-ignore` comment.

## Requirements

Fix these type issues in `components/slider/index.tsx`:

1. Remove the `// @ts-ignore` comment that precedes the RcSlider component. The component should type-check without any type suppression comments.

2. In the `onInternalChangeComplete` function, eliminate the `as any` type assertion used on `nextValues`. The code should compile without suppressing the type error through `as any`.

3. The `restProps` spread on RcSlider should be handled in a way that avoids the type conflict with the component's internal callback handling. TypeScript should understand that `onAfterChange` and `onChange` are not part of the spread.

## Verification

After your changes:
- `npx tsc --noEmit` should pass without errors
- `npx eslint components/slider/index.tsx` should pass
- `npx biome lint components/slider/index.tsx` should pass
- `npx jest --config .jest.js components/slider/__tests__/type.test.tsx` should pass
- `npx jest --config .jest.js components/slider/__tests__/index.test.tsx` should pass
- The file should not contain `// @ts-ignore` comments
- The file should not use `as any` type assertions in the `onInternalChangeComplete` function

## Context

This is a TypeScript-only change. No runtime behavior should change. Focus on achieving type safety through proper type casting rather than type suppression.