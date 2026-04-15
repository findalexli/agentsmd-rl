# Add `head` parameter to `gr.HTML` for third-party library support

## Problem

The `gr.HTML` component supports templates, CSS, and JavaScript via `html_template`, `css_template`, and `js_on_load`, but there's no way to load external JavaScript or CSS libraries (like Chart.js, D3, or Three.js) that the component's JavaScript depends on. Users who need third-party libraries have no mechanism to inject `<script>` or `<link>` tags into the document `<head>`.

## Requirements

### Code changes in `gradio/components/html.py`

The `HTML` class needs a new `head` parameter for injecting raw HTML into the document head. The component's existing publishing and Hub-upload methods already accept a `head` argument for the head content — the new instance-level parameter should serve as a fallback when those methods are called without an explicit `head` value:

- **Constructor parameter**: Add `head: str | None = None` to the `HTML.__init__` signature, positioned before `server_functions`.

- **Instance attribute**: Store the `head` value on the instance so the serialization and publishing methods can reference it as a fallback.

- **Publishing and Hub-upload fallback**: The existing methods that serialize the component for publishing and for pushing to the Hub each take a `head` parameter. When that argument is falsy or not provided, these methods should fall back to the instance attribute value set during construction.

### Documentation changes

1. **API reference** — `.agents/skills/gradio/SKILL.md`:
   - The HTML component signature must include `head: str | None = None`, appearing before `server_functions` in the parameter list.

2. **Usage guide** — `guides/03_building-with-blocks/06_custom-HTML-components.md`:
   - Add a section about the `head` parameter and loading third-party scripts
   - Reference third-party library loading
   - Include a code example using `gr.HTML` with `head=` and a `<script>` tag to load an external library such as Chart.js

## Relevant files

- `gradio/components/html.py` — HTML component implementation
- `.agents/skills/gradio/SKILL.md` — Component API reference
- `guides/03_building-with-blocks/06_custom-HTML-components.md` — Usage guide
