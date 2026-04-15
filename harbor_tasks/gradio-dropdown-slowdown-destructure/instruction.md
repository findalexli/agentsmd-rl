# Fix: Massive dropdown slowdowns from reactive variable access

## Problem

Opening a dropdown with hundreds of elements causes the browser tab to freeze for 5-10 seconds on first use after page load. Profiling shows massive amounts of component updates triggered by accessing variables that are part of a derived computation.

The issue appears to be related to how `input_text`, `selected_index`, and `selected_indices` are declared in `js/dropdown/shared/Dropdown.svelte`. These variables are currently involved in a reactive declaration pattern that causes cascading re-computations when `selected_index` is accessed repeatedly (once per `DropdownOption` rendered), resulting in O(N) redundant computations.

## Expected Behavior

- Dropdown with hundreds of elements should open instantly without freezing
- The variables `input_text`, `selected_index`, and `selected_indices` should be declared in a way that avoids triggering redundant re-derivations when accessed
- The template should use stable references instead of creating new array references on each access

## Files to Investigate

- `js/dropdown/shared/Dropdown.svelte` -- investigate the `input_text`, `selected_index`, and `selected_indices` variable declarations and how they interact with the reactive system

## Technical Context

Svelte 5 handles certain patterns of array destructuring from derived values poorly. When variables are derived together and then accessed repeatedly (once per rendered option), the derivation chain re-runs, causing O(N) redundant computations. The fix requires restructuring how these variables are declared and updated to avoid this cascade.

The current implementation uses a pattern that combines `input_text` and `selected_index` in a single derivation. The template also computes `selected_indices` inline as `selected_index === null ? [] : [selected_index]`, which creates a new array reference on every access, amplifying the reactive cascades.
