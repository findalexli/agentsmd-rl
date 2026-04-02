# Feature Request: Reactive prop observation in `gr.HTML` `js_on_load`

## Context

Gradio's `gr.HTML` component supports a `js_on_load` parameter that runs JavaScript when the component loads. Inside this script, you can modify component props via `props.value = ...` and trigger events via `trigger('click')`. However, there is currently **no way to react to prop changes** that come from Python event listeners (i.e., when the component is used as an output).

For example, a developer might want to fire a `submit` event when a counter value reaches a threshold, but the value is being incremented by a Python backend function. Today there's no reactive mechanism in `js_on_load` to observe when `props.value` changes due to a backend update.

## Problem

In `js/html/shared/HTML.svelte`, the `js_on_load` function receives `element`, `trigger`, `props`, `server`, and `upload` — but no way to observe when props change from backend updates. The props update effect in `HTML.svelte` silently syncs values without notifying user code.

Additionally, in `js/html/Index.svelte`, the value derivation uses the `||` operator (`gradio.props.value || ""`), which incorrectly treats falsy values like `0` or `""` as empty — this should use nullish coalescing (`??`) instead.

## Expected Behavior

1. A `watch` function should be available inside `js_on_load` that lets developers register callbacks for specific prop changes triggered by Python event listeners:
   ```js
   // Watch a single prop
   watch('value', () => {
       console.log('value is now:', props.value);
   });

   // Watch multiple props
   watch(['value', 'color'], () => {
       console.log('value or color changed');
   });
   ```

2. Watch callbacks should fire **after** the template has re-rendered with the new prop values (so reading `props.value` inside the callback returns the updated value).

3. Falsy values like `0` should be correctly preserved as the component value.

## Files to Modify

- `js/html/Index.svelte` — Define the watch registration and notification logic, fix value coalescing, pass watch capability to the shared component
- `js/html/shared/HTML.svelte` — Accept the watch capability as a prop, expose it in the `js_on_load` Function scope, invoke notifications when props change from backend
- `gradio/components/html.py` — Update the `js_on_load` docstring to document the new `watch` function

## Constraints

- Watch callbacks should only fire for changes coming from Python event listeners (backend), not for changes made from JavaScript
- Watch callbacks should fire after template re-render so `props` reflect updated values inside the callback
- Errors in watch callbacks should be caught and logged, not crash the component
