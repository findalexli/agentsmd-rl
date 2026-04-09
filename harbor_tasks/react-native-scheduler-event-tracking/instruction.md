# React Native Fabric renderer missing event information in scheduler tracks

## Problem

The React Native Fabric renderer's event tracking functions in `ReactFiberConfigFabric.js` are stubs that return hardcoded default values. Specifically:

- `trackSchedulerEvent()` is a no-op — it does nothing when called during event dispatch.
- `resolveEventType()` always returns `null` — it never reports the actual event type (e.g., `"click"`, `"keydown"`).
- `resolveEventTimeStamp()` always returns `-1.1` — it never reports the actual event timestamp.

This means React scheduler performance traces in React Native lack event timing information entirely. The DOM renderer already has working implementations of these functions, but the React Native (Fabric) renderer does not.

## Expected Behavior

- `trackSchedulerEvent()` should capture the current event from `global.event` so it can be distinguished from subsequent events.
- `resolveEventType()` should return the type of the current `global.event` (if it differs from the tracked scheduler event). It needs to handle both modern events (with a `.type` property) and legacy React Native events (which use `dispatchConfig.phasedRegistrationNames` instead of `.type`). For legacy events with a name like `"onTouchStart"`, the `"on"` prefix should be stripped and the result lowercased.
- `resolveEventTimeStamp()` should return the `.timeStamp` of the current `global.event` (if it differs from the tracked scheduler event), falling back to `-1.1` when there is no event.

## Files to Look At

- `packages/react-native-renderer/src/ReactFiberConfigFabric.js` — the Fabric renderer's fiber host config, where the three event tracking functions are defined
