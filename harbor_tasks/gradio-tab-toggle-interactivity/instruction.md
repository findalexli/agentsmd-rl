# Bug: Tab interactive property changes ignored for non-active tabs

## Summary

When a Gradio `Tabs` component uses lazy mounting (non-active tabs are not mounted until selected for performance), programmatic updates to a tab's `interactive` property are silently lost if the tab has not yet been mounted.

For example, if a tab starts with `interactive=False` and a button click handler later sets it to `interactive=True`, the tab button remains disabled because the update never reaches the tab button rendered by the parent `Tabs` component.

## Reproduction

```python
import gradio as gr

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.Tab("Main"):
            gr.Markdown("Main content")
        with gr.Tab("Locked", id="locked", interactive=False) as locked_tab:
            gr.Markdown("This tab was unlocked!")

    unlock_btn = gr.Button("Unlock Tab")
    unlock_btn.click(lambda: gr.Tab(interactive=True), outputs=locked_tab)

demo.launch()
```

1. Launch the app
2. The "Locked" tab button is disabled (correct)
3. Click "Unlock Tab"
4. **Expected**: The "Locked" tab becomes enabled and clickable
5. **Actual**: The tab button stays disabled — the `interactive=True` update was ignored

## Root Cause

The issue is in the frontend state management. When `update_state` receives new props for a component, it updates the component's internal state. However, for non-mounted tab items, the tab *button* is rendered by the parent `Tabs` component using an `initial_tabs` array that was set at initialization time. Updating the tabitem's props doesn't propagate back to the parent `Tabs` component's `initial_tabs`, so the button never reflects the change.

## Affected Files

- `js/core/src/init.svelte.ts` — the `update_state` method in the `AppTree` class
- `js/tabs/shared/Tabs.svelte` — the `Tabs` component that renders tab buttons

## Expected Behavior

After the fix, programmatically updating a tab's `interactive`, `visible`, or `label` properties should take effect immediately — even if the tab has not yet been selected/mounted. The tab button in the navigation bar should reflect the updated state.
