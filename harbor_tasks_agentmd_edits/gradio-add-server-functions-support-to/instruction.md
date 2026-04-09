# Add server functions support to gr.HTML

## Problem

The `gr.HTML` component supports `js_on_load` for running JavaScript when the component loads. However, there's no way to call Python functions from this JavaScript code. Users need to be able to call backend Python functions directly from their `js_on_load` scripts.

For example, users want to do something like:
```python
def list_files(path):
    return os.listdir(path)

gr.HTML(
    js_on_load="""
        const files = await server.list_files("/path");
        // use files in the DOM
    """,
    server_functions=[list_files],
)
```

Currently, this is not possible because:
1. The `HTML` component doesn't accept a `server_functions` parameter
2. The `server` object is not available in `js_on_load`

## Expected Behavior

1. Add a `server_functions` parameter to `gr.HTML` that accepts a list of Python functions
2. When `server_functions` is provided, each function should be decorated with `@server` (from `gradio.components.base`) and attached to the component instance
3. The `server` object should be passed through to the frontend Svelte components (`js/html/Index.svelte` and `js/html/shared/HTML.svelte`)
4. In `HTML.svelte`, the `server` object should be available as a parameter in the `js_on_load` function (passed to `new Function()`)
5. Update the `js_on_load` docstring in the Python component to document the availability of the `server` object
6. Update `.agents/skills/gradio/SKILL.md` to document the new `server_functions` feature (add parameter to `HTML` signature and add a new section about Server Functions)

## Files to Look At

- `gradio/components/html.py` — the HTML component class
- `js/html/Index.svelte` — main Svelte component wrapper
- `js/html/shared/HTML.svelte` — shared HTML component logic
- `.agents/skills/gradio/SKILL.md` — agent skill documentation

## Key Implementation Details

- Import `server` from `gradio.components.base` in `html.py`
- The `server_functions` parameter should be `list[Callable] | None = None`
- For each function in `server_functions`, decorate with `server(fn)`, set as attribute, and append to `self.server_fns`
- In Svelte, the server object comes from `gradio.shared.server`
- Pass `server` to the `new Function("element", "trigger", "props", "server", js_on_load)` call

## Files to Modify

1. `gradio/components/html.py` — add parameter and logic
2. `js/html/Index.svelte` — pass server to shared component
3. `js/html/shared/HTML.svelte` — add server to js_on_load execution
4. `.agents/skills/gradio/SKILL.md` — document the feature
