# Bug: Load event values lost for components in inactive tabs

## Summary

When `demo.load()` targets a component that lives inside an inactive `gr.Tab`, the value set by the load event is silently lost. When the user later clicks on the tab to reveal the component, it appears empty instead of showing the expected value.

## Reproduction

```python
import gradio as gr

with gr.Blocks() as demo:
    with gr.Tab('Tab 1'):
        with gr.Row():
            gr.Chatbot()
            with gr.Column():
                gr.Slider()
                gr.Slider()
                gr.Slider()

    with gr.Tab('Tab 2'):
        textbox = gr.Textbox(label="Output")

    demo.load(
        fn=lambda: 'some text',
        inputs=None,
        outputs=textbox,
    )

if __name__ == "__main__":
    demo.launch()
```

1. Launch the app above
2. Wait for it to load (the `demo.load` event fires on startup)
3. Click "Tab 2"
4. **Expected**: The textbox shows "some text"
5. **Actual**: The textbox is empty

## Technical Requirements

The fix must address three related issues in `js/core/src/init.svelte.ts`:

### 1. Deferred state storage for unmounted components

When `update_state` is called for a component that has not yet mounted (no `_set_data` callback available), the implementation must store the update in a deferred state map using the exact pattern:
- A private class field named `#pending_updates` initialized as `new Map<number, Record<string, unknown>>()`
- The `update_state` method must read existing pending state via `this.#pending_updates.get(id)`
- The `update_state` method must write merged state via `this.#pending_updates.set(id, { ...existing, ...new_state })`

### 2. Deferred state application on component registration

When a component eventually mounts and registers via `register_component`, the implementation must apply any pending updates that were stored while the component was hidden. The fix must use this exact pattern:
- Read pending state via `this.#pending_updates.get(id)`
- Delete the entry via `this.#pending_updates.delete(id)` after reading
- Defer application using `tick().then(() => { ... })` to ensure Svelte 5 effects have run first
- Apply the pending state by calling `_set(pending)` with the stored data

### 3. In-place property modification instead of spread replacement

In `update_state`, when modifying a node's props, the implementation must modify properties in-place using `for...in` loops instead of replacing the entire props object with spread syntax. The fix must use:
- `for (const key in new_props.shared_props)` to update shared props in-place
- `for (const key in new_props.props)` to update component props in-place

This prevents Svelte 5's deep `$state` proxy from losing track of values during async component mounting.

### 4. Targeted node lookup in render visibility handling

When handling visibility changes for previously hidden children, the implementation must use targeted node lookup instead of full tree traversal with root reassignment. The fix must:
- Use `find_node_by_id(this.root!, id)` for targeted lookup
- Check `#hidden_on_startup.has(node.id)` before any processing to enable early return when no changes are needed
- Avoid patterns like `this.root = this.traverse(this.root, ...)` which trigger unnecessary reactive cascades

## Key Files

- `js/core/src/init.svelte.ts` — Contains the state management logic that needs modification
