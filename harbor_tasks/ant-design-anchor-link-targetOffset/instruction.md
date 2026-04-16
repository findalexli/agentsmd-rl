# Task: Add per-link targetOffset support to Anchor.Link component

## Problem Description

The `Anchor` component currently only supports a global `targetOffset` prop that applies the same scroll offset to all links. Users need the ability to specify different scroll offsets for individual `Anchor.Link` items.

For example, in a documentation page, clicking different anchor links may need to scroll to different positions relative to their targets - the first heading might need a 64px offset while subsequent headings need only 32px.

## Required Behavior

### 1. AnchorLink accepts targetOffset prop

The `AnchorLinkBaseProps` interface must accept an optional numeric `targetOffset` property.

**Expected:** The interface includes `targetOffset?: number` as an optional property.

### 2. Context interface supports per-link targetOffset

The context interface used by Anchor and AnchorLink must be updated so that:
- `registerLink` accepts an optional second parameter for the link's target offset
- `scrollTo` accepts an optional second parameter for the link's target offset

**Expected:** Both methods have signatures that accept `(link: string, targetOffset?: number) => void`.

### 3. Per-link offsets are tracked

The `Anchor` component must maintain a mapping that stores each link's targetOffset value keyed by its href string.

**Expected:** A mapping of type `Record<string, number>` tracks per-link offsets, initialized empty.

### 4. Links communicate their targetOffset to parent

When an `AnchorLink` component mounts or its targetOffset prop changes, it must communicate the current targetOffset value to the parent `Anchor` component via the context's `registerLink` function.

**Expected:** Registration is reactive - changing an `AnchorLink`'s targetOffset prop after mounting updates the stored value. The registration call includes both the href and the targetOffset.

### 5. Scroll offset precedence

When calculating the scroll offset for a clicked link, the system must use this precedence (highest to lowest):
1. The per-link targetOffset associated with the clicked link
2. The global targetOffset prop from the Anchor component
3. The offsetTop prop from the Anchor component
4. 0 (default fallback)

**Expected:** The scroll offset calculation respects this precedence order using nullish coalescing.

### 6. Active link detection uses per-link offsets

The active link detection logic (which determines which link is highlighted based on scroll position) must respect individual link offsets. The function that determines the active anchor must:
- Accept a mapping of per-link offsets as a parameter
- For each link, look up its individual offset from the mapping
- Fall back to the global offsetTop when no individual offset exists

**Expected:** Active link detection considers per-link offsets with fallback to global offset.

### 7. Cleanup on unmount

When an `AnchorLink` unmounts, the parent `Anchor` component must remove that link's entry from the per-link offsets mapping to prevent memory leaks.

**Expected:** The cleanup removes the link's stored offset from the mapping.

### 8. Click handler passes targetOffset

When a user clicks an `AnchorLink`, the component must pass its `targetOffset` prop value to the context's `scrollTo` function.

**Expected:** The click handler includes the link's targetOffset when invoking scroll navigation.

## Testing Requirements

The existing test suite must pass after implementation. Run the following to verify:
- `npm run lint:biome` - Biome lint check must pass
- `npx eslint components/anchor/ --cache` - ESLint must pass with no errors
- `NODE_OPTIONS='--max-old-space-size=4096' npx tsc --noEmit --skipLibCheck` - TypeScript must compile
- `npm test -- --testPathPatterns=anchor --no-coverage` - Anchor component tests must pass

## Implementation Notes

- Follow existing code style in the repository
- Ensure TypeScript types are precise with no `any` types
- The feature must be backward compatible - existing code without per-link targetOffset should continue to work unchanged
- Use optional chaining (`?.`) when calling context methods
