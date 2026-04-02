# gr.HTML does not support custom event names

## Bug Description

The `gr.HTML` component in Gradio supports triggering events from JavaScript via `trigger('event_name', data)` in the `js_on_load` parameter. However, only the predefined set of Gradio events (like `click`, `change`, etc.) can be attached as Python listeners. If a developer triggers a custom event name (e.g., `trigger('keypress', {key: e.key})`) from their JavaScript code, there is no way to attach a Python listener for it — calling `component.keypress(fn, ...)` raises an `AttributeError` because `keypress` is not in the standard event list.

This is a significant limitation for the `gr.HTML` component, which is designed to be a flexible building block for custom interactive components. Developers should be able to define arbitrary event names in their JavaScript and wire them up to Python handlers.

## Relevant Files

- `gradio/components/html.py` — The `HTML` component class definition
- `gradio/events.py` — Contains `EventListener` class and `all_events` list

## Expected Behavior

If a custom event name appears (in quotes) in the `js_on_load` string of an `HTML` component, calling `component.custom_event_name(fn, inputs, outputs)` should work the same way as any built-in event listener — wiring a Python function to be called when the JavaScript `trigger('custom_event_name', data)` fires.

## Steps to Reproduce

```python
import gradio as gr

with gr.Blocks() as demo:
    keyboard = gr.HTML(
        js_on_load="""
        document.addEventListener('keydown', (e) => {
            trigger('keypress', {key: e.key});
        });
        """,
    )
    textbox = gr.Textbox(label="Key pressed")

    def get_key(evt_data: gr.EventData):
        return evt_data.key

    # This raises AttributeError: 'HTML' object has no attribute 'keypress'
    keyboard.keypress(get_key, None, textbox)
```
