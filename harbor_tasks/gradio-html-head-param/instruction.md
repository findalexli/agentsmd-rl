# Add `head` parameter to gr.HTML for third-party library support

## Problem

The `gr.HTML` component supports templates, CSS, and JavaScript via `html_template`, `css_template`, and `js_on_load`, but there's no way to load external JavaScript or CSS libraries (like Chart.js, D3, or Three.js) that the component's JavaScript depends on. Users who need third-party libraries have no mechanism to inject `<script>` or `<link>` tags into the document `<head>`.

## What to do

1. **Add a `head` parameter** to `gradio/components/html.py`:
   - Add `head: str | None = None` to `HTML.__init__()` (before `server_functions`)
   - Store it as `self.head` in `__init__`
   - Update `_to_publish_format()` to use `self.head` as fallback when no explicit `head` argument is passed
   - Update `push_to_hub()` similarly so the component's head value is preserved when publishing

2. **Update the component documentation** in `.agents/skills/gradio/SKILL.md`:
   - The HTML component signature must include the new `head` parameter with its type annotation

3. **Update the custom HTML guide** at `guides/03_building-with-blocks/06_custom-HTML-components.md`:
   - Add a new section documenting the `head` parameter
   - Include a code example showing how to load a third-party library (e.g., Chart.js) using the head parameter

## Relevant files

- `gradio/components/html.py` — HTML component implementation
- `.agents/skills/gradio/SKILL.md` — Component API reference
- `guides/03_building-with-blocks/06_custom-HTML-components.md` — Usage guide

## Notes

- The `head` content should be injected into the document `<head>` before `js_on_load` runs, so the loaded libraries are available to the component's JavaScript
- Scripts should be deduplicated by `src` attribute so multiple components sharing the same library only load it once
- Follow the existing code patterns in `html.py` for parameter handling
