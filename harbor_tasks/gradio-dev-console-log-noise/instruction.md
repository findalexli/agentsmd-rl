# Unwanted console.log Statements in Dev Server

## Bug Description

Several debug `console.log` statements were accidentally left in the frontend source code. They produce noisy output in the dev server console that clutters the developer experience and provides no useful information.

The affected areas are:

1. **`js/core/src/MountCustomComponent.svelte`** — Inside the `$effect()` block, there is a `console.log` that dumps internal reactive state (`el`, `comp`, `runtime`) on every effect re-run. This fires repeatedly during normal component mounting and adds significant noise.

2. **`js/preview/src/plugins.ts`** — Inside the `make_gradio_plugin` function's `load()` hook, there is a `console.log("init gradio")` that fires every time the virtual module `cc-init` is loaded during development. This is a leftover initialization trace.

3. **`js/spa/src/main.ts`** — At the top of the `get_index()` function, there is a `console.log("mode", mode)` that logs the application mode on every page load. This was likely used during development of the custom component mode feature.

## Expected Behavior

The dev server console should not contain these debug log statements. They add noise and make it harder to spot genuine warnings or errors during development.

## Task

Remove the unwanted `console.log` statements from the three affected files without altering any other functionality.
