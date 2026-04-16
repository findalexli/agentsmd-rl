# Add Per-Link targetOffset Support to Anchor Component

## Problem

The Anchor component currently supports a global `targetOffset` prop that sets the scroll offset for all anchor links. However, users need the ability to set different scroll offsets for individual links.

For example, when a page has varying fixed header heights at different sections, each anchor link should be able to specify its own offset from the top of the viewport when scrolling to that section.

## Current Behavior

- `Anchor` component accepts `targetOffset` prop that applies to all links
- All `Anchor.Link` items use the same global offset when clicked
- Active link detection during scroll also uses the same global offset

## Expected Behavior

1. Each `Anchor.Link` should accept its own `targetOffset` prop with type `number | undefined`
2. When a link-level `targetOffset` is provided, it should take precedence over the global one
3. If a link doesn't specify `targetOffset`, it should fall back to the global `targetOffset`
4. When a user clicks an `Anchor.Link`, the scrolling should use the link-specific offset if set
5. Active link detection during scroll (highlighting the current section) should respect per-link offsets
6. When a link is removed/unmounted, any stored per-link offset should be cleaned up

## Files to Modify

- `components/anchor/Anchor.tsx` - Main Anchor component with `AntAnchor` interface and scroll logic
- `components/anchor/AnchorLink.tsx` - AnchorLink component and `AnchorLinkBaseProps` interface
