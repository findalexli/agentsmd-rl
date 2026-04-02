# Browser Test Event Dispatch Broken

## Bug Summary

Component events don't fire properly in Gradio's browser test infrastructure. Several issues in the test rendering utilities and the core `Gradio` class prevent events from being dispatched and listened to during tests.

## Problem Details

### 1. Event Dispatcher Overridden to No-Op

In `js/utils/src/utils.svelte.ts`, the `Gradio` class constructor has a code path that unconditionally overrides the event dispatcher with a no-op function when running outside the browser or in test mode. This causes:
- The component registration callback is never invoked
- The dispatcher function provided via shared props is replaced with a no-op
- Component events (change, input, submit, etc.) are silently swallowed

Look at the constructor of the `Gradio` class for an early-return that short-circuits initialization.

### 2. Test Render Utility Missing Key Functions

In `js/tootils/src/render.ts`, the `render()` function's return type promises event helper functions, but:
- The event listening functions are never defined or returned
- The mock dispatcher dispatches DOM `CustomEvent`s but nothing actually listens for them
- There's no way to programmatically update component data from tests or read it back
- The component registration callback is a no-op, so the component's data bridge is never established

The render function needs proper event infrastructure: a function to listen for events that returns a mock/spy, a dispatcher that notifies those listeners, and data mutation functions wired through component registration.

### 3. Clipboard Copy Crashes

In `js/textbox/shared/Textbox.svelte`, the copy handler calls the Clipboard API without any error handling. If the API throws (e.g., due to missing permissions in a test environment), the entire function crashes and the copy feedback animation is never shown.

### 4. IconButtonWrapper Prop Mismatch

In `js/textbox/shared/Textbox.svelte`, the `IconButtonWrapper` component receives the custom button click handler, but the prop name used doesn't match what `IconButtonWrapper` expects. The handler isn't wired up, so custom button click events are silently dropped.

### 5. Vitest Config: Browser Permissions

In `js/spa/vite.config.ts`, browser permissions (camera, microphone, clipboard) are configured in the wrong location — they're set on the browser instance instead of the Playwright provider's context options. This means clipboard-related tests fail due to missing permissions.

## Files to Investigate

- `js/utils/src/utils.svelte.ts` — `Gradio` class constructor
- `js/tootils/src/render.ts` — Test rendering utility
- `js/textbox/shared/Textbox.svelte` — Textbox component
- `js/spa/vite.config.ts` — Vitest browser test configuration
- `js/tootils/src/index.ts` — Tootils barrel export
