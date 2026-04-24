# Add `head` parameter to `gr.HTML` for third-party library support

## Problem

The `gr.HTML` component supports templates, CSS, and JavaScript via `html_template`, `css_template`, and `js_on_load`, but there's no way to load external JavaScript or CSS libraries (like Chart.js, D3, or Three.js) that the component's JavaScript depends on. Users who need third-party libraries have no mechanism to inject `<script>` or `<link>` tags into the document `<head>`.

When the HTML component is serialized for publishing or pushing to the Hub, the existing `_to_publish_format` and `push_to_hub` methods accept a `head` argument. However, users cannot set a default `head` value at component construction time. When these methods are called without an explicit `head` value, the component should be able to fall back to an instance-level default.

## Requirements

### Code changes in `gradio/components/html.py`

The `HTML` class needs a new `head` parameter for injecting raw HTML into the document head, with type annotation `str | None = None`. This parameter must appear before `server_functions` in the `__init__` signature.

The component's publishing and Hub-upload methods already accept a `head` argument for the head content — the new instance-level parameter should serve as a fallback when those methods are called without an explicit `head` value. The fallback logic in both `_to_publish_format` and `push_to_hub` should follow the pattern: `head or self.head` (where `self.head` is the instance attribute set during construction).

**Required behavior:**

- **Constructor parameter**: The `HTML.__init__` method must accept a `head` parameter with type `str | None = None`, positioned in the signature before `server_functions`.

- **Instance attribute**: The `head` value passed to `__init__` must be stored as an instance attribute named `self.head` so that serialization and publishing methods can reference it as a fallback.

- **Publishing fallback**: In `_to_publish_format`, when the method's `head` parameter is not provided (falsy), the method must fall back to the instance's `self.head` attribute.

- **Hub-upload fallback**: In `push_to_hub`, when the method's `head` parameter is not provided (falsy), the method must pass the instance's `self.head` as the fallback value to `_to_publish_format`.

### Documentation changes

1. **API reference** — `.agents/skills/gradio/SKILL.md`:
   - The HTML component signature must include `head: str | None = None`, appearing before `server_functions` in the parameter list.

2. **Usage guide** — `guides/03_building-with-blocks/06_custom-HTML-components.md`:
   - Add a section titled "Loading Third-Party Scripts with head"
   - Mention loading third-party libraries (such as Chart.js) via the `head` parameter
   - Include a code example using `gr.HTML` with `head=` containing a `<script>` tag to load an external library (such as `https://cdn.jsdelivr.net/npm/chart.js`)
   - Show a `js_on_load` example that uses the loaded library

## Relevant files

- `gradio/components/html.py` — HTML component implementation
- `.agents/skills/gradio/SKILL.md` — Component API reference
- `guides/03_building-with-blocks/06_custom-HTML-components.md` — Usage guide

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
