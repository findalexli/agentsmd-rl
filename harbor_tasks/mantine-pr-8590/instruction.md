# Mantine Popover SubMenu Overlap Bug

## Context

Mantine's Popover component uses `@floating-ui/react` for positioning. The positioning pipeline uses **middleware** that transform the floating element's position step by step. Two key middlewares are:

- **`flip`**: Changes the placement side (e.g., `bottom` → `top`) when the element would overflow a viewport edge
- **`shift`**: Slides the element along an axis to keep it within viewport bounds without changing the side

## The Bug

When a `Menu` component (which uses Popover) is positioned near a screen edge, and it has a `SubMenu`, the SubMenu incorrectly overlaps the parent Menu instead of flipping to the opposite side.

When both `flip` and `shift` are enabled (the default), the current middleware ordering causes `shift` to run before `flip`. Since `shift` pushes the element into the visible viewport area first, `flip` never detects an overflow and therefore never triggers to flip the element to the opposite side.

This is contrary to floating-ui's own documentation, which recommends applying `flip` before `shift` for edge-aligned placements.

## What to Fix

Find the `getPopoverMiddlewares` function in `packages/@mantine/core/src/components/Popover/use-popover.ts`.

When both `flip` and `shift` are enabled, the relative ordering of these two middlewares in the array needs to match floating-ui's recommended pattern. The correct end result is that when you examine the built middleware array, `flip` appears before `shift`.

## Verification

After fixing, run the Popover tests:

```bash
cd /workspace/mantine
yarn jest --testPathPatterns Popover --no-coverage
```

The Popover Jest tests must pass, and ESLint, Prettier, and Stylelint for the Popover directory must all be clean.