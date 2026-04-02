# Bug: All components in nested tabs and closed accordions are pre-loaded on startup

## Description

When a Gradio app uses nested `gr.Tabs` (tabs inside tabs) and `gr.Accordion` components, **all** child components are pre-loaded and pre-rendered at startup — even those in non-selected sub-tabs and closed accordions. This causes unnecessary resource usage and slower initial load times.

The expected behavior is that only components in the currently-selected tab path and open accordions should be loaded initially. Components in non-selected sub-tabs and closed accordions should be lazily loaded when the user navigates to them.

## Affected Files

- `js/core/src/_init.ts` — the `determine_visible_components` function handles initial visibility determination. It correctly handles top-level tabs but does not account for accordion components or nested tab selection.
- `js/core/src/init.svelte.ts` — the `make_visible_if_not_rendered` function is called when previously invisible children need to be rendered (e.g., when switching tabs). It currently recurses unconditionally into all children without respecting tab selection or accordion open/closed state.

## How to Reproduce

Create an app with nested tabs and a closed accordion:

```python
import gradio as gr

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.Tab("Set 1"):
            with gr.Tabs():
                with gr.Tab("Tab 1"):
                    gr.Textbox(label="Input 1")
                with gr.Tab("Tab 2"):
                    gr.Textbox(label="Input 2")
            gr.Textbox(label="Input 3")
        with gr.Tab("Set 2"):
            with gr.Tabs():
                with gr.Tab("Tab 11"):
                    gr.Textbox(label="Input 11")
                with gr.Tab("Tab 12"):
                    gr.Textbox(label="Input 12")
        with gr.Tab("Set 3"):
            with gr.Accordion("Details", open=False):
                gr.Textbox(label="Input 14")

demo.launch()
```

On initial load, ALL inputs (Input 1 through Input 14) are pre-loaded and rendered, even though only "Set 1 > Tab 1" content (Input 1 and Input 3) should be visible and loaded.

## Expected Behavior

1. On initial load, only components in the selected tab path should be pre-loaded
2. Components in closed accordions should not be pre-loaded (unless the accordion is the direct target)
3. When switching to a new tab, only the selected sub-tab's components should be rendered — not all sub-tabs
