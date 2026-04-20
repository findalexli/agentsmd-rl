# Task: Add per-link targetOffset support to Anchor.Link component

## Problem Description

The `Anchor` component currently only supports a global `targetOffset` prop that applies the same scroll offset to all links. Users need the ability to specify different scroll offsets for individual `Anchor.Link` items.

For example, in a documentation page, clicking different anchor links may need to scroll to different positions relative to their targets - the first heading might need a 64px offset while subsequent headings need only 32px.

## Required Behavior

### 1. AnchorLink accepts targetOffset prop

The `AnchorLinkBaseProps` interface in `components/anchor/AnchorLink.tsx` must accept an optional numeric `targetOffset` property.

**Expected:** The interface includes `targetOffset?: number` as an optional property.

### 2. Context interface supports per-link targetOffset

The context interface in `components/anchor/Anchor.tsx` used by Anchor and AnchorLink must be updated so that:
- `registerLink` accepts an optional second parameter named `targetOffset` of type `number`
- `scrollTo` accepts an optional second parameter named `targetOffset` of type `number`

**Expected:** Both methods have signatures matching `(link: string, targetOffset?: number) => void`.

### 3. Per-link offsets are tracked

The `Anchor` component must declare a ref named `linkTargetOffsetRef` to store per-link offsets:
- Type: `Record<string, number>`
- Initial value: empty object `{}`
- Declaration: `const linkTargetOffsetRef = React.useRef<Record<string, number>>({})`

**Expected:** The `linkTargetOffsetRef` stores each link's targetOffset value keyed by its href string.

### 4. Links communicate their targetOffset to parent

When an `AnchorLink` component mounts or its targetOffset prop changes, it must communicate the current targetOffset value to the parent `Anchor` component via the context's `registerLink` function:
- The call uses optional chaining: `registerLink?.(href, targetOffset)`
- The useEffect dependency array is `[href, targetOffset]` to re-register when targetOffset changes

**Expected:** Registration is reactive - changing an `AnchorLink`'s targetOffset prop after mounting updates the stored value via the registerLink call with both href and targetOffset.

### 5. Register implementation stores targetOffset

The `registerLink` implementation in `components/anchor/Anchor.tsx` must store the targetOffset when provided:
- Parameter name: `newTargetOffset`
- Storage condition: `if (newTargetOffset !== undefined)`
- Storage pattern: `linkTargetOffsetRef.current[link] = newTargetOffset`

**Expected:** The registerLink function stores the provided targetOffset in the linkTargetOffsetRef mapping when defined.

### 6. Scroll offset precedence

When calculating the scroll offset for a clicked link, the `handleScrollTo` callback must use this precedence (highest to lowest):
1. The per-link targetOffset parameter named `targetOffsetParams`
2. The global targetOffset prop from the Anchor component
3. The offsetTop prop from the Anchor component
4. 0 (default fallback)

**Expected:** The calculation uses: `const finalTargetOffset = targetOffsetParams ?? targetOffset ?? offsetTop ?? 0`

### 7. Active link detection uses per-link offsets

The active link detection logic (which determines which link is highlighted based on scroll position) must respect individual link offsets via the `getInternalCurrentAnchor` function in `components/anchor/Anchor.tsx`:
- The function accepts a fourth parameter named `_linkTargetOffset` of type `Record<string, number>`
- For each link, it calculates the offset using: `const linkOffsetTop = _linkTargetOffset?.[link] ?? _offsetTop`
- The function is called with `linkTargetOffsetRef.current` as the fourth argument

**Expected:** Active link detection considers per-link offsets with fallback to global offset.

### 8. Cleanup on unmount

When an `AnchorLink` unmounts, the parent `Anchor` component must remove that link's entry from the per-link offsets mapping to prevent memory leaks:
- Cleanup pattern: `delete linkTargetOffsetRef.current[link]`

**Expected:** The unregisterLink function removes the link's stored offset from linkTargetOffsetRef.

### 9. Click handler passes targetOffset

When a user clicks an `AnchorLink`, the component must pass its `targetOffset` prop value to the context's `scrollTo` function:
- The call uses optional chaining: `scrollTo?.(href, targetOffset)`

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
