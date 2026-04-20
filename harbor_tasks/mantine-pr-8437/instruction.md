# Menu.Sub openDelay Prop Task

## Problem Description

The `Menu.Sub` component in `@mantine/core` does not support an `openDelay` prop, even though the underlying `useDelayedHover` hook already accepts this parameter.

**Symptom:** When you pass `openDelay={500}` to `Menu.Sub`, TypeScript reports an error that `openDelay` is not a known prop. If the TypeScript error is suppressed, the delay value is ignored and the submenu opens immediately (0ms delay).

**Expected behavior:** `Menu.Sub` should accept an `openDelay` prop (just like it already accepts `closeDelay`). When provided, it should control how many milliseconds to wait before opening the submenu on hover. A default value of `0` maintains backwards compatibility.

## What You Need to Do

Fix the `Menu.Sub` component so that the `openDelay` prop is properly accepted and used.

## Files to Modify

- `packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx`
- `packages/@docs/demos/src/demos/core/Menu/Menu.demo.sub.tsx`
- `packages/@mantine/core/src/components/Menu/Menu.story.tsx`

## Verification

After your fix:
- TypeScript should accept `openDelay` as a valid prop on `Menu.Sub`
- The `openDelay` value should be passed to the `useDelayedHover` hook (not ignored/hardcoded)
- A default of `0` should be used when the prop is not provided
- The demo file `Menu.demo.sub.tsx` should use `openDelay=` on `Menu.Sub` components
- The story file `Menu.story.tsx` should use `openDelay=` on `Menu.Sub` components

## References

- The `useDelayedHover` hook in `packages/@mantine/core/src/utils/Floating/` already accepts `openDelay` parameter
- `closeDelay` prop on `Menu.Sub` for reference on how timing props are implemented
