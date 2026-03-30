# Fix: Massive dropdown slowdowns from destructuring a derived array

## Problem

Opening a dropdown with hundreds of elements causes the browser tab to freeze for 5-10 seconds on first use after page load. Profiling shows massive amounts of component updates triggered by accessing the `selected_indices` array.

## Root Cause

In the Dropdown component (`js/dropdown/shared/Dropdown.svelte`), the variables `input_text` and `selected_index` are destructured from a `$derived.by()` return value:

```js
let [input_text, selected_index] = $derived.by(() => { ... });
```

Svelte 5 handles array destructuring of derived values poorly in this case. Every time `selected_index` is accessed (which happens once per `DropdownOption` rendered), the entire derivation chain re-runs. With hundreds of options, this causes a cascade of redundant reactive computations.

Additionally, `selected_indices` is computed inline in the template as `selected_index === null ? [] : [selected_index]`, which creates a new array reference on every access, further amplifying the reactive update cascade.

## Expected Behavior

- Dropdown with hundreds of elements should open instantly without freezing
- `input_text` and `selected_index` should be `$state()` variables updated via `$effect()` instead of destructured from `$derived.by()`
- `selected_indices` should be a `$derived` value, not computed inline

## Files to Investigate

- `js/dropdown/shared/Dropdown.svelte` -- the `input_text`, `selected_index`, and `selected_indices` variable declarations
