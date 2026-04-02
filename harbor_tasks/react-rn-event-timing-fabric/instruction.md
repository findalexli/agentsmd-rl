# React Native Event Timing in Fabric Renderer

## Problem

The React Native Fabric renderer's event tracking functions don't actually extract event timing information from the global event object. Currently:

- `trackSchedulerEvent()` is a no-op
- `resolveEventType()` always returns `null`
- `resolveEventTimeStamp()` always returns `-1.1`

This prevents React's performance profiling tools from capturing meaningful event timing data in React Native applications using the Fabric renderer.

## Expected Behavior

The functions should:
1. `trackSchedulerEvent()` should capture the current global event for reference
2. `resolveEventType()` should extract and return the event type string from `global.event`, handling both modern `event.type` property and legacy `dispatchConfig.phasedRegistrationNames` format used by React Native
3. `resolveEventTimeStamp()` should extract `event.timeStamp` from the global event
4. Both resolution functions should avoid returning data from the same event captured by `trackSchedulerEvent()` to prevent self-referencing

## Files to Modify

- `packages/react-native-renderer/src/ReactFiberConfigFabric.js`

Look for the exported functions `trackSchedulerEvent`, `resolveEventType`, and `resolveEventTimeStamp` near the end of the file.

## Notes

- React Native events may use a legacy format where the event type is stored in `dispatchConfig.phasedRegistrationNames.bubbled` or `.captured` instead of a direct `type` property
- Event type strings in the legacy format may be prefixed with "on" (e.g., "onClick") and should be normalized to lowercase without the prefix (e.g., "click")
- The functions should maintain their existing Flow type signatures
