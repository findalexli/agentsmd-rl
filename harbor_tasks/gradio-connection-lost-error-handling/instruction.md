# Fix: Error modals accumulate when server connection is lost

## Problem

When a Gradio app has a timer event that periodically fires requests to the backend, and the server goes down, the frontend shows a cascade of empty error modals -- one for each failed request. These error modals accumulate rapidly, filling the screen and providing a poor user experience.

The previous behavior (in Gradio 5.x) was to show a single "connection lost" error and automatically try to reconnect, reloading the page when the server comes back up.

## Root Cause

The frontend error handling code in three files does not distinguish between regular errors and connection errors:

1. `client/js/src/utils/submit.ts` -- When POST requests or SSE connections fail due to a broken connection, the error events do not include a `broken` flag to indicate this is a connection issue rather than an application error.

2. `js/core/src/dependency.ts` -- The `DependencyManager` class does not track connection-lost state. Each error from a broken connection creates a new error modal, and events continue dispatching even after the connection is lost.

3. `js/core/src/Blocks.svelte` -- There is no centralized connection-lost handler that would show a single error message and start a reconnection loop.

## Expected Fix

1. In `submit.ts`: Detect connection errors (matching `BROKEN_CONNECTION_MSG`) and set the `broken` flag on error events.
2. In `dependency.ts`: Add a `connection_lost` flag that stops event dispatching after a connection error is detected, and add a callback for notifying the Blocks component.
3. In `Blocks.svelte`: Add a `handle_connection_lost` function that shows a single error modal and starts a reconnection interval that reloads the page when the server recovers.

## Files to Investigate

- `client/js/src/utils/submit.ts` -- error event firing logic
- `js/core/src/dependency.ts` -- `DependencyManager` class
- `js/core/src/Blocks.svelte` -- error handling and reconnection logic
