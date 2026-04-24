# ChatInterface fill_height no longer fills the browser viewport

## Bug Description

`ChatInterface(fill_height=True)` (the default) no longer fills the browser viewport in Gradio 6.x. The chatbot area stays at a fixed ~400px height instead of expanding to fill available space.

This regression was introduced during the Svelte 5 migration. The fill_height configuration is not being properly propagated from the backend to the frontend layout system.

## Expected Behavior

1. When `ChatInterface(fill_height=True)` is created, the internal Chatbot component should not have a hardcoded height of 400 pixels. The height should be determined by the Chatbot's own default, allowing CSS flex layout to expand it to fill the viewport.

2. The `fill_height` property from the app configuration must propagate to the frontend and influence the root column's `scale` property. When `fill_height` is true, the root column should have `scale` set to expand and fill available space.

3. The frontend TypeScript `AppConfig` interface must include `fill_height` as a property so the configuration can be properly typed and passed through.

4. The config object passed to the frontend AppTree and its `reload()` method must include the `fill_height` property.

## Reproduction

```python
import gradio as gr

def echo(message, history):
    return f"Echo: {message}"

demo = gr.ChatInterface(fn=echo, fill_height=True)
demo.launch()
```

The chatbot area should expand to fill the browser viewport, but instead stays at a fixed height.

## Scope

This issue involves the backend ChatInterface component and the frontend initialization code that handles app configuration and layout.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `prettier (JS/TS/JSON/Markdown formatter)`
