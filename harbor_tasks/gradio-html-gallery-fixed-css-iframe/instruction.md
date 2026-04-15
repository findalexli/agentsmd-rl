# HTML Gallery: Components with `position: fixed` break page layout

## Bug Description

The Gradio website has an HTML Components Gallery at `js/_website/src/routes/custom-components/html-gallery/`. When community-contributed custom HTML components use `position: fixed` in their CSS, the gallery page layout breaks — the fixed-position elements escape the component preview area and overlay the rest of the page, covering navigation and other components.

Additionally, components that use the `@children` slot placeholder in their `html_template` render as empty because the gallery never passes any child content to them.

## Where to look

- `js/_website/src/routes/custom-components/html-gallery/+page.svelte` — the main gallery page, renders components in both the grid and the maximized modal view
- `js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte` — individual component card in the gallery grid
- `js/_website/src/routes/custom-components/html-gallery/utils.ts` — shared utility functions for the gallery

## Required Changes

### 1. Utils.ts Functions

Create these exported functions in `utils.ts` with exactly these signatures:

- **`needs_iframe(css_template: string | undefined): boolean`** — Returns `true` if the CSS contains `position: fixed` (case-insensitive, tolerant of whitespace variations like `position:  fixed`), otherwise `false`. Must handle `undefined`, `null`, and empty string inputs gracefully without throwing.

- **`build_srcdoc(component, props, dark): string`** — Builds a self-contained HTML document for iframe rendering. Arguments:
  - `component`: object with `html_template: string`, `css_template: string`, `js_on_load?: string | null`, `head?: string | null`, `default_props: Record<string, any>`
  - `props`: `Record<string, any>` of property values to render into templates
  - `dark`: `boolean` indicating dark mode

  Returns a complete HTML document string containing:
  - `<!DOCTYPE html>` declaration
  - `<html>` with `class="dark"` when `dark=true`
  - `<meta charset="utf-8">`
  - Theme CSS in a `<style>` block (imported from `$lib/assets/theme.css?raw`)
  - Component CSS rendered via template literal substitution
  - Component `head` content included if present
  - Rendered `html_template` in the body
  - `js_on_load` script with props available via a `Proxy` object
  - **Critical**: To prevent XSS, escape `</script` by replacing it with `<\\/script` in both the props JSON and the JS content

- **`clickOutside(element: HTMLDivElement, callbackFunction: () => void)`** — Existing Svelte action that must be preserved. Returns an object with `update` and `destroy` methods. Adds click listener to `document.body`, calls callback when click occurs outside the element, cleans up on destroy.

### 2. Svelte Component Updates

Both `+page.svelte` and `ComponentEntry.svelte` must:

- Import `needs_iframe` and `build_srcdoc` from `./utils`
- Import `theme` from `$lib/stores/theme` for dark mode detection
- Import `BaseButton` from `@gradio/button` for the children slot
- Detect when a component's `css_template` needs iframe isolation via `needs_iframe()`
- For iframe components: render an `<iframe sandbox="allow-scripts">` with `srcdoc` set via `build_srcdoc(component, props, is_dark)`
- For components with `@children` in `html_template`: pass child content (a `BaseButton` with text "Click Me") to the `BaseHTML` component via slots

### 3. Guide Documentation

Update `guides/03_building-with-blocks/06_custom-HTML-components.md` to document:

- The `push_to_hub` method for sharing components with the HTML Components Gallery
- The `head` parameter of `push_to_hub` — required when component uses external libraries (e.g., `head='<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'`)
- Authentication requirements: HuggingFace write token (via `token` parameter or `huggingface-cli login`)

## Expected Behavior

1. Components with `position: fixed` CSS are rendered inside sandboxed iframes instead of inline, preventing layout breakage
2. Components whose template includes `@children` receive default child content (a button with text "Click Me") so they render meaningfully
3. Iframe rendering includes proper theme support (dark/light mode classes applied to the `<html>` element) and the component's head scripts
4. Guide documents how to share components via `push_to_hub` including the `head` parameter for external dependencies and authentication via HuggingFace token or CLI login
