# Tab labels not translated when using i18n

## Bug Description

When using Gradio's `I18n` feature with `gr.Tab`, the tab labels are not translated according to the selected language. Other components like `gr.Button` translate correctly, but the tab strip shows the raw i18n key instead of the translated string.

## Reproduction

```python
import gradio as gr

i18n = gr.I18n(
    en={"lion": "Lion", "tiger": "Tiger"},
    es={"lion": "Leon", "tiger": "Tigre"},
)
with gr.Blocks() as demo:
    with gr.Tab(i18n("lion")):
        gr.Button(i18n("lion"))
    with gr.Tab(i18n("tiger")):
        gr.Button(i18n("tiger"))
demo.launch(i18n=i18n)
```

When switching to Spanish, the buttons show "Leon" and "Tigre" but the tabs still show "Lion" and "Tiger" (the English/default values).

## Expected Behavior

Tab labels should be translated just like other component labels when i18n is active and the user switches languages. When no i18n is configured, raw labels should be preserved for backward compatibility.

## Technical Details

The tab collection logic lives in `js/core/src/init.svelte.ts`, specifically in the `_gather_initial_tabs` function. Tab nodes have a `props.props.i18n` field (an optional translation function that maps string → string) and a `props.shared_props.label` field (the raw label string).

The function produces an `initial_tabs` object mapping parent tab ID → array of tab descriptor objects. Each tab descriptor is an object with keys: `label`, `id`, `elem_id`, `visible`, `interactive`, `scale`, `component_id`.

When `node.props.props.i18n` is present, the tab's `label` field should be produced by calling `i18n(raw_label)`. When no i18n function is present, the raw label should be used as-is.