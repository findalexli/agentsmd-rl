# Apply component filters on initial DevTools load

## Problem

React DevTools currently relies on the `window.__REACT_DEVTOOLS_COMPONENT_FILTERS__` global variable to apply saved component filters when the extension loads. This approach has several issues:

1. **Filters don't apply until the frontend connects.** On initial page load, the backend doesn't know about saved filters until the DevTools frontend sends them over the bridge via `overrideComponentFilters`. This means the full component tree is always built first, then immediately reconciled when filters arrive — wasting work on every page load.

2. **The standalone DevTools injects filters as a separate script tag** prepended before the backend script. This is fragile and creates ordering dependencies.

3. **React Native has no sync storage**, so it always falls back to default filters, ignoring any user customization.

## Expected Behavior

Component filters should be passed directly to `initialize()` so they're available *before* React renders. The `initialize` function in `packages/react-devtools-core/src/backend.js` should accept component filters (as an array or Promise) and pass them through `installHook()` and down to the fiber renderer's `attach()` function, which should apply them immediately instead of reading from a global.

The `overrideComponentFilters` bridge message and `__REACT_DEVTOOLS_COMPONENT_FILTERS__` global mechanism should be removed from the backend.

## Files to Look At

- `packages/react-devtools-core/src/backend.js` — `initialize()` function signature and `connectToDevTools()`
- `packages/react-devtools-core/src/standalone.js` — how the standalone server injects backend + filters
- `packages/react-devtools-shared/src/hook.js` — `installHook()` passes config to renderers
- `packages/react-devtools-shared/src/attachRenderer.js` — bridges hook to renderer
- `packages/react-devtools-shared/src/backend/fiber/renderer.js` — `attach()` applies component filters
- `packages/react-devtools-shared/src/devtools/store.js` — frontend store filter management
- `packages/react-devtools-extensions/src/contentScripts/` — extension messaging for settings + filters

After making the code changes, update `packages/react-devtools-core/README.md` to document the new `initialize()` parameters and the component filter type specifications. The README currently only documents the `settings` parameter — the new filter-related parameters and their types should be documented as well.
