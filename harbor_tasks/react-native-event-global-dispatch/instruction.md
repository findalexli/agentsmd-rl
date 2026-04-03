# Set global.event During React Native Event Dispatch

In React Native's legacy event system, the `executeDispatch` function in `packages/react-native-renderer/src/legacy-events/EventPluginUtils.js` does not set `global.event` during event handler execution. This differs from browser behavior where `window.event` (i.e., `global.event`) is automatically set to the current event being dispatched.

Some event handlers and libraries rely on `global.event` being available during dispatch. Without it, these handlers cannot access the current event object through the global reference.

Fix `executeDispatch` to save the current `global.event`, set it to the event being dispatched before calling the listener, and restore the previous value after the listener completes (ensuring proper nesting behavior for recursive dispatches).
