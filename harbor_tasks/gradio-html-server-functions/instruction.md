# Add server_functions support to gr.HTML

## Problem

The gr.HTML component needs to accept a list of Python functions that can be exposed to custom HTML components. Currently, there is no way to pass server-side functions to the HTML component.

## Expected Behavior

Add a `server_functions` parameter to `gr.HTML` that accepts a list of Python functions. The component should:

1. Accept and store the `server_functions` parameter (defaulting to `None` when not provided)
2. Include `server_functions` information when converted to a string representation - the output must contain the literal string "server_functions" and the function names (accessible via the function's `__name__` attribute) when functions are present

For example, given:
```python
def my_server_func():
    return "result"

html = gr.HTML(value="test", server_functions=[my_server_func])
```

Converting the HTML object to a string (via `str(html)` or `print(html)`) should produce output that contains both:
- The literal string "server_functions"
- The function name "my_server_func"

## Files to Look At

- `gradio/components/html.py` — The HTML component definition
- `.agents/skills/gradio/SKILL.md` — Agent skill documentation (must be updated to reflect the new parameter in the HTML component section)

## Documentation Requirements

When updating `.agents/skills/gradio/SKILL.md`, document the `server_functions` parameter within the HTML component signature section. The HTML component documentation section uses a header with the format:

```
### `HTML(`
```

Add the `server_functions` parameter to the documented signature within this section.
