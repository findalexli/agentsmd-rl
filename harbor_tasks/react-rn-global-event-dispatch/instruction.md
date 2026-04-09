# Expose event as global variable during React Native dispatch

## Problem

In the React Native renderer's legacy event system, `global.event` is not set to the currently dispatched event during listener execution. On the web, browsers expose `window.event` (i.e., `global.event`) pointing to the active event while a listener runs, and React Native's new `EventTarget` implementation also does this. However, the legacy `executeDispatch` function in the React Native renderer does not follow this convention.

This means code that accesses `global.event` during an event handler callback gets `undefined` (or a stale value) instead of the event currently being dispatched.

## Expected Behavior

When `executeDispatch` calls a listener, `global.event` should reference the event being dispatched for the duration of that listener's execution. If `global.event` already held a value before the dispatch (e.g., from a parent dispatch or prior code), it must be restored after the listener completes, preserving correct behavior for nested dispatches.

## Files to Look At

- `packages/react-native-renderer/src/legacy-events/EventPluginUtils.js` — contains the `executeDispatch` function that calls event listeners
