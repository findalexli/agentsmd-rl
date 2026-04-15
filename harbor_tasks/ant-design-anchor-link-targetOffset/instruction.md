# Task: Add per-link targetOffset support to Anchor.Link component

## Problem Description

The `Anchor` component currently only supports a global `targetOffset` prop that applies the same scroll offset to all links. Users need the ability to specify different scroll offsets for individual `Anchor.Link` items.

For example, in a documentation page, clicking different anchor links may need to scroll to different positions relative to their targets - the first heading might need a 64px offset while subsequent headings need only 32px.

## Required Behavior

### 1. AnchorLink accepts targetOffset prop

The `AnchorLinkBaseProps` interface in `components/anchor/AnchorLink.tsx` must accept an optional numeric `targetOffset` property.

**Test asserts:** `export interface AnchorLinkBaseProps { ... targetOffset?: number ... }`

### 2. Context interface supports per-link targetOffset

The `AntAnchor` interface in `components/anchor/Anchor.tsx` must be updated so that:
- `registerLink` accepts an optional second parameter: signature must match `registerLink: (link: string, targetOffset?: number) => void`
- `scrollTo` accepts an optional second parameter: signature must match `scrollTo: (link: string, targetOffset?: number) => void`

**Test asserts:** The exact type signatures above must be present in the code.

### 3. Per-link offsets are tracked

The `Anchor` component must maintain a mapping that stores each link's targetOffset value keyed by its href string. The storage mechanism must:
- Use a type of `Record<string, number>` for the mapping
- Be initialized as an empty mapping

**Test asserts:** `Record<string, number>` type is used; the mapping is initialized empty.

### 4. Links communicate their targetOffset to parent

When an `AnchorLink` component mounts or its targetOffset prop changes, it must communicate the current targetOffset value to the parent `Anchor` component via the context's `registerLink` function.

The registration must be reactive - changing an `AnchorLink`'s targetOffset prop after mounting must update the stored value. The useEffect that calls `registerLink` must have a dependency array that includes both `href` and `targetOffset`.

**Test asserts:** The useEffect dependency array contains `[href, targetOffset]`; `registerLink?.(href, targetOffset)` is called.

### 5. Scroll offset precedence

When calculating the scroll offset for a clicked link, the system must use this precedence (highest to lowest):
1. The per-link targetOffset associated with the clicked link
2. The global targetOffset prop from the Anchor component
3. The offsetTop prop from the Anchor component
4. 0 (default fallback)

**Test asserts:** The calculation uses nullish coalescing to implement this precedence: `targetOffsetParams ?? targetOffset ?? offsetTop ?? 0`

### 6. Active link detection uses per-link offsets

The active link detection logic (which determines which link is highlighted based on scroll position) must respect individual link offsets. The function that determines the active anchor must:
- Accept a mapping of per-link offsets as a parameter with type `Record<string, number>`
- For each link, look up its individual offset from the mapping
- Fall back to the global offsetTop when no individual offset exists
- Use nullish coalescing for the fallback

**Test asserts:** The function signature accepts `_linkTargetOffset?: Record<string, number>`; the calculation uses `_linkTargetOffset?.[link] ?? _offsetTop` pattern.

### 7. Cleanup on unmount

When an `AnchorLink` unmounts, the parent `Anchor` component must remove that link's entry from the per-link offsets mapping to prevent memory leaks.

**Test asserts:** The cleanup code deletes entries from the mapping: `delete mapping[link]`

### 8. Click handler passes targetOffset

When a user clicks an `AnchorLink`, the component must pass its `targetOffset` prop value to the context's `scrollTo` function.

**Test asserts:** The click handler calls `scrollTo?.(href, targetOffset)`.

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
