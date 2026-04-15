# Fix: Error modals accumulate when server connection is lost

## Problem

When a Gradio app has a timer event that periodically fires requests to the backend, and the server goes down, the frontend shows a cascade of empty error modals -- one for each failed request. These error modals accumulate rapidly, filling the screen and providing a poor user experience.

The previous behavior (in Gradio 5.x) was to show a single "connection lost" error and automatically try to reconnect, reloading the page when the server comes back up.

## Required Behaviors

After the fix, the following behaviors must be implemented:

1. **Connection error detection in `client/js/src/utils/submit.ts`**: The code must detect when an error matches the constant `BROKEN_CONNECTION_MSG` (defined in `client/js/src/constants.ts`). When such an error occurs, the error event must include a `broken` flag set to a variable named `is_connection_error` that dynamically compares the error to `BROKEN_CONNECTION_MSG`.

2. **Connection state tracking in `js/core/src/dependency.ts`**: The `DependencyManager` class must:
   - Track connection state using a property named `connection_lost` initialized to `false`
   - Check for `result.broken` in error handlers
   - Set `this.connection_lost = true` when broken errors are detected
   - Accept a callback parameter named `on_connection_lost_cb` and invoke it when connection is lost
   - Stop dispatching new events when connection is lost (short-circuit the `dispatch()` method)

3. **Reconnection handling in `js/core/src/Blocks.svelte`**:
   - Define a function named `handle_connection_lost` that shows a single error modal with title "Connection Lost" and the `LOST_CONNECTION_MESSAGE` constant
   - Use `setInterval` to periodically poll the server status via `app.reconnect()`
   - When `reconnect()` returns "connected" or "changed", reload the page via `window.location.reload()`
   - Pass `handle_connection_lost` as an argument to the `DependencyManager` constructor
   - Store the interval ID in a variable named `reconnect_interval`
   - Clean up the interval using `clearInterval(reconnect_interval)` when the component is destroyed

## Files to Investigate

- `client/js/src/utils/submit.ts` -- POST request and SSE connection error handling
- `client/js/src/constants.ts` -- contains `BROKEN_CONNECTION_MSG` and `LOST_CONNECTION_MESSAGE`
- `js/core/src/dependency.ts` -- `DependencyManager` class event dispatching
- `js/core/src/Blocks.svelte` -- error handling and UI state management

## Verification Criteria

The fix must satisfy these test assertions:
- `is_connection_error` variable dynamically compares errors to `BROKEN_CONNECTION_MSG`
- Error events have `broken: is_connection_error` (not hardcoded `false`)
- `connection_lost` property exists and is initialized to `false`
- `dispatch()` method checks `this.connection_lost` and returns early when true
- `result.broken` is checked in error handlers
- `on_connection_lost_cb` callback is accepted and invoked
- `handle_connection_lost` function is defined in Blocks.svelte
- `setInterval`, `.reconnect()`, and `location.reload()` are used for reconnection
- `reconnect_interval` state variable exists
- `clearInterval(reconnect_interval)` is called during cleanup
