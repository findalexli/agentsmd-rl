# Bug: `launch(debug=False)` still creates a debug-enabled FastAPI app

## Summary

When calling `demo.launch(debug=False)` (or relying on the default `debug=False`), the resulting FastAPI application still has `debug=True`. This means that even when users explicitly disable debug mode, the app runs with debug enabled — leaking stack traces, enabling debug middleware, etc.

## Reproduction

```python
import gradio as gr

demo = gr.Interface(lambda x: x, "text", "text")
demo.launch(debug=False)
# The FastAPI app at demo.server_app still has .debug == True
```

You can verify this programmatically:

```python
from gradio import routes, Interface

app = routes.App.create_app(Interface(lambda x: x, "text", "text"))
print(app.debug)  # Expected: False, Actual: True
```

## Relevant Files

- `gradio/routes.py` — the `App.create_app()` static method
- `gradio/blocks.py` — the `Blocks.launch()` method that calls `create_app()`

## Expected Behavior

The `debug` parameter passed to `launch()` should be forwarded through to the FastAPI `App` constructor, so that `App.debug` reflects the caller's intent. By default, `create_app()` should produce a non-debug app.
