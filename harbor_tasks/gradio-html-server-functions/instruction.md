# Add server_functions support to gr.HTML

## Problem

The gr.HTML component currently supports custom HTML templates with JavaScript interactivity via `js_on_load`, but it cannot directly call server-side Python functions from that JavaScript. Users need a way to expose specific Python functions to their custom HTML components so they can fetch data from the backend.

## Expected Behavior

Add a `server_functions` parameter to `gr.HTML` that accepts a list of Python functions. These functions should be callable from within the `js_on_load` script via a `server` object. For example:

```python
def list_files(path):
    return os.listdir(path)

gr.HTML(
    html_template="<div>...</div>",
    js_on_load="""
        const files = await server.list_files('/some/path');
        // files contains the result from the Python function
    """,
    server_functions=[list_files],
)
```

## Files to Look At

- `gradio/components/html.py` — The HTML component definition
- `.agents/skills/gradio/SKILL.md` — Agent skill documentation (must be updated to reflect the new parameter)

## Additional Requirements

After implementing the code changes, update the `.agents/skills/gradio/SKILL.md` file to document the new `server_functions` parameter in the HTML component signature, consistent with the existing documentation style.
