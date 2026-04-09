# Task: Add per-link targetOffset to Anchor.Link component

## Problem

The `Anchor` component currently only supports a global `targetOffset` prop that applies to all links equally. Users need the ability to set different scroll offsets for individual `Anchor.Link` items.

## Goal

Add a `targetOffset` prop to `Anchor.Link` that allows each link to have its own scroll offset value. When a link has its own `targetOffset`, it should take precedence over the global `targetOffset` from the `Anchor` component.

## Files to Modify

1. **`components/anchor/AnchorLink.tsx`** - Add `targetOffset` prop to the component and interface
2. **`components/anchor/Anchor.tsx`** - Update the context interface and logic to handle per-link offsets

## Key Requirements

1. **Interface Update**: `AnchorLinkBaseProps` should have an optional `targetOffset?: number` property

2. **Context Interface**: Update `AntAnchor` interface:
   - `registerLink` should accept an optional `targetOffset` parameter
   - `scrollTo` should accept an optional `targetOffset` parameter

3. **Storage**: The `Anchor` component needs to track per-link offsets. Add a ref to store `Record<string, number>` mapping link hrefs to their targetOffsets.

4. **Registration**: When `AnchorLink` mounts or updates:
   - Pass its `targetOffset` to `registerLink`
   - Include `targetOffset` in the useEffect dependency array

5. **Scroll Behavior**: When a link is clicked:
   - `AnchorLink` should pass its `targetOffset` to `scrollTo`
   - `handleScrollTo` in `Anchor.tsx` should use the link-level offset with this precedence: `linkOffset > globalTargetOffset > offsetTop > 0`

6. **Active Link Detection**: The `getInternalCurrentAnchor` function needs to:
   - Accept the per-link offsets map as a parameter
   - Use link-level offset when calculating if a section is active (with fallback to global offset)

7. **Cleanup**: When a link unmounts, clean up its stored targetOffset.

## Testing

The existing test suite should pass after your changes. Look at `components/anchor/__tests__/Anchor.test.tsx` for reference on how anchor behavior is tested.

## Notes

- Follow the existing code style in the repository
- Ensure TypeScript types are precise (no `any` types)
- The feature should be backward compatible - existing code without per-link targetOffset should work unchanged
- Version for new API: 6.4.0 (if updating documentation)
