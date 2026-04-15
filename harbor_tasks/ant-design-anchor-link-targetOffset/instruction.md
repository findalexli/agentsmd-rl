# Task: Add per-link targetOffset to Anchor.Link component

## Problem

The `Anchor` component currently only supports a global `targetOffset` prop that applies to all links equally. Users need the ability to set different scroll offsets for individual `Anchor.Link` items. For example, in a documentation page, the first heading might need a 64px offset while subsequent headings need only 32px.

## Goal

Add a `targetOffset` prop to `Anchor.Link` that allows each link to have its own scroll offset value. When a link has its own `targetOffset`, it should take precedence over the global `targetOffset` from the `Anchor` component.

## Files to Modify

1. **`components/anchor/AnchorLink.tsx`** - Add `targetOffset` prop to the component and interface
2. **`components/anchor/Anchor.tsx`** - Update the context interface and logic to handle per-link offsets

## Required Changes

### 1. Interface Update (AnchorLink.tsx)

The `AnchorLinkBaseProps` interface must include an optional `targetOffset?: number` property.

### 2. Context Interface Update (Anchor.tsx)

The `AntAnchor` interface must be updated:
- `registerLink` must accept an optional second parameter: `targetOffset?: number`
- `scrollTo` must accept an optional second parameter: `targetOffset?: number`

### 3. Storage Mechanism (Anchor.tsx)

The `Anchor` component must store per-link offsets. Declare a ref that maps link hrefs (strings) to their targetOffset values (numbers). The type should be `Record<string, number>`.

### 4. Registration (AnchorLink.tsx)

When `AnchorLink` mounts or updates:
- Pass its `targetOffset` to the `registerLink` context function
- The useEffect that calls `registerLink` must depend on both `href` and `targetOffset` so re-registration occurs when targetOffset changes

### 5. Scroll Behavior (Anchor.tsx)

When a link is clicked, the scroll offset calculation must follow this precedence:
1. The link's own targetOffset (passed to scrollTo)
2. The global targetOffset from Anchor props
3. The offsetTop from Anchor props
4. Default to 0

### 6. Active Link Detection (Anchor.tsx)

The `getInternalCurrentAnchor` function must:
- Accept the per-link offsets map as a parameter
- When checking if a section is active, use the link-level offset if available, otherwise fall back to the global offset
- Pass the per-link offsets map when calling this function

### 7. Cleanup (Anchor.tsx)

When a link unmounts (in `unregisterLink`), the stored targetOffset for that link must be removed from the per-link offsets map to prevent memory leaks.

### 8. AnchorLink Click Handler (AnchorLink.tsx)

When an AnchorLink is clicked, it must pass its `targetOffset` to the `scrollTo` context function.

## Testing

The existing test suite should pass after your changes. Look at `components/anchor/__tests__/Anchor.test.tsx` for reference on how anchor behavior is tested.

## Notes

- Follow the existing code style in the repository
- Ensure TypeScript types are precise (no `any` types)
- The feature should be backward compatible - existing code without per-link targetOffset should work unchanged
- Version for new API: 6.4.0 (if updating documentation)
