# Task: Fix TypeScript Types in Slider Component

## Problem Description

The Slider component (`components/slider/index.tsx`) has suboptimal TypeScript type handling that should be improved for better type safety:

1. **Issue with `onChangeComplete`**: The current code uses `as any` casting when calling the `onChangeComplete` callback:
   ```typescript
   onChangeComplete?.(nextValues as any);
   ```
   This bypasses TypeScript's type checking and should be replaced with a proper type assertion.

2. **Issue with `restProps`**: The code uses `@ts-ignore` to suppress type errors when spreading `restProps` to `RcSlider`:
   ```typescript
   // @ts-ignore
   <RcSlider
     {...restProps}
   ```
   This hides potential type mismatches and should be replaced with explicit type handling.

## What You Need to Do

Fix both type issues in `components/slider/index.tsx`:

1. Replace the `as any` cast in `onChangeComplete` with a proper type assertion that uses `RcSliderProps['onChangeComplete']`

2. Remove the `@ts-ignore` comment before `RcSlider` and add a proper type assertion for `restProps` using `Omit<SliderProps, 'onAfterChange' | 'onChange'>`

## Files to Modify

- `components/slider/index.tsx` - The main Slider component implementation

## Hints

- Look for the `onInternalChangeComplete` function to find the first issue
- Look for the JSX return statement with `<RcSlider` to find the second issue
- The proper type for `onChangeComplete` is available from `RcSliderProps`
- The `restProps` type should explicitly exclude conflicting event handlers
- Run `npx tsc --noEmit` to verify your changes compile correctly

## Verification

Your changes should:
1. Pass TypeScript compilation without slider-related errors
2. Remove all use of `as any` for type casting in the affected code
3. Remove the `@ts-ignore` comment
4. Maintain the existing runtime behavior of the component
