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

## Relevant Code

The issue is in `js/core/src/init.svelte.ts`, specifically in the `_gather_initial_tabs` function. This function collects tab metadata to seed the `Tabs` component, but it does not apply the i18n translation function to the tab labels. Each tab node has access to an i18n function via its props, but the function gathers the raw label value without translating it.

## Expected Behavior

Tab labels should be translated just like other component labels when i18n is active and the user switches languages.
