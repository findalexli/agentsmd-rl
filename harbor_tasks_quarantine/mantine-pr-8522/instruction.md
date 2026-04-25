# Mantine SSR Fix Task

## Context

In Next.js App Router with React 19, SSR errors occur when using components like `Tooltip`, `Popover.Target`, `HoverCard.Target`, and `MenuTarget`. These components receive children that can be a React `Lazy` type (created with `React.lazy()`), which lacks a proper `props` structure at SSR time.

When these components call `cloneElement` on a lazy child and try to access `.props`, the SSR fails because lazy elements don't have their props resolved until render time.

## Problem Behavior

The current implementation uses `isElement(children)` to check validity, but this returns `true` for lazy elements. When the component then tries to access `children.props` or call `cloneElement(children)`, it crashes in SSR contexts.

Example error that occurs:
- `Tooltip` wraps a `React.lazy(() => import('./Component'))`
- SSR tries to access `.props` on the lazy element
- Error: Cannot read properties of (lazy value)

## Expected Fix

Create a new utility function called `getSingleElementChild` in `packages/@mantine/core/src/core/utils/get-single-element-child/get-single-element-child.ts` that:

1. Uses `Children.toArray()` to normalize children (handles fragments, arrays, etc.)
2. Returns `null` if there isn't exactly one element child
3. Returns the single element child

Then update these components to use this utility instead of direct `isElement` checks:
- `ComboboxEventsTarget.tsx`
- `ComboboxTarget.tsx`
- `FocusTrap.tsx`
- `HoverCardTarget.tsx`
- `MenuTarget.tsx`
- `PopoverTarget.tsx`
- `Tooltip.tsx`
- `TooltipFloating.tsx`

Also add the export to `packages/@mantine/core/src/core/utils/index.ts`.

## Testing the Fix

After applying the fix, run the Tooltip test suite to verify everything still works:
```bash
npm run jest -- --testPathPatterns Tooltip --passWithNoTests
```

All 44 existing tests should pass.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
