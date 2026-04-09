# Add head= support to gr.HTML component

The `gr.HTML` component needs to support a new `head=` parameter that allows users to inject custom scripts, styles, and other HTML content into the `<head>` section of the document. This is useful for integrating third-party libraries like Chart.js.

## Code Changes Required

Update the Python `gr.HTML` component in `gradio/components/html.py`:

1. Add `head: str | None = None` parameter to `HTML.__init__()`
2. Pass the `head` parameter to the parent class via `super().__init__()` so it's included in the component config

Update the frontend TypeScript/Svelte component in `js/html/shared/HTML.svelte`:

1. Accept the `head` prop in the component's props interface

## Documentation Update Required

Update the agent skill documentation in `.agents/skills/gradio/SKILL.md`:

1. Update the HTML component signature to include the `head: str | None = None` parameter
2. The signature should be updated to reflect the new parameter (place it after `buttons` and before `server_functions` to match the Python signature order)

## Example Usage

```python
import gradio as gr

chart_html = gr.HTML(
    value=[30, 70, 45, 90, 60],
    html_template='<canvas id="chart"></canvas>',
    js_on_load="""
    const canvas = element.querySelector('#chart');
    new Chart(canvas, { type: 'bar', data: { ... } });
    """,
    head='<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
)
```

After making the code changes, ensure the SKILL.md file is updated to document the new parameter in the HTML component signature.
