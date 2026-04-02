# Gallery component ignores custom height and has broken CSS styles

## Problem

The Gradio `Gallery` component has two related bugs that prevent the gallery from rendering at a user-specified height:

1. **CSS class name mismatch in `js/gallery/shared/Gallery.svelte`**: The component's template binds a container element to a class name, but the corresponding CSS style block defines rules under a *different* class name. As a result, critical styles (e.g., `height: 100%` on the container, sizing rules for images and buttons) are never applied.

2. **Height value not propagated correctly**: When a non-numeric height value (such as a CSS string like `"300px"`) is passed to the Gallery, it is silently dropped at multiple points:
   - The `height` prop type in `js/gallery/shared/Gallery.svelte` and `js/gallery/types.ts` only allows `number | "auto"`, so string CSS values are rejected.
   - In `js/gallery/Index.svelte`, the height is only forwarded when it is a `number`, meaning any valid CSS string height is lost.
   - The inline `style:height` binding in `Gallery.svelte` unconditionally appends `"px"` to non-`"auto"` values, which corrupts string heights that already include units.
   - The file upload wrapper area has no height styling, so even when the gallery container has a height, the upload area inside it collapses.

## Expected behavior

- The gallery container's CSS styles should actually apply to the rendered element.
- Users should be able to pass CSS string heights (e.g., `"300px"`, `"50vh"`) and have them respected.
- The upload wrapper should fill its parent height so the interactive area doesn't collapse.

## Files to investigate

- `js/gallery/Index.svelte` — height prop forwarding and upload wrapper styling
- `js/gallery/shared/Gallery.svelte` — height type, inline style logic, CSS class definitions
- `js/gallery/types.ts` — GalleryProps type definition
