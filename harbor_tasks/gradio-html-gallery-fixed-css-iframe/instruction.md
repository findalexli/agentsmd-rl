# HTML Gallery: Components with `position: fixed` break page layout

## Bug Description

The Gradio website has an HTML Components Gallery at `js/_website/src/routes/custom-components/html-gallery/`. When community-contributed custom HTML components use `position: fixed` in their CSS, the gallery page layout breaks — the fixed-position elements escape the component preview area and overlay the rest of the page, covering navigation and other components.

Additionally, components that use the `@children` slot placeholder in their `html_template` render as empty because the gallery never passes any child content to them.

## Where to look

- `js/_website/src/routes/custom-components/html-gallery/+page.svelte` — the main gallery page, renders components in both the grid and the maximized modal view
- `js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte` — individual component card in the gallery grid
- `js/_website/src/routes/custom-components/html-gallery/utils.ts` — shared utility functions for the gallery

## Expected Behavior

1. Components with `position: fixed` CSS should be isolated so they don't break the surrounding page layout. An iframe with sandboxed rendering would prevent their CSS from affecting the parent page.
2. Components whose template includes `@children` should receive some default child content (e.g., a button) so they render meaningfully in the gallery.
3. The iframe rendering should include proper theme support (dark/light mode) and the component's head scripts.

## Reproduction

Visit the HTML gallery page and add a component whose `css_template` contains `position: fixed`. The element will overlay the entire page instead of staying within its preview card. Similarly, add a component with `@children` in its `html_template` — it will render as blank.

## Additional Context

The guide at `guides/03_building-with-blocks/06_custom-HTML-components.md` should also document the `push_to_hub` method for sharing components with the gallery, including authentication requirements and the `head` parameter.
