## Bug Description

The `timeStamp` property handling in React Native's SyntheticEvent has two issues that cause incorrect timing data for native events.

### Issue 1: Non-monotonic timestamps

Currently, when an event doesn't explicitly provide a `timeStamp`, the code falls back to `Date.now()`. This is inconsistent with web platform behavior where `timeStamp` should be a monotonic timestamp (similar to what `performance.now()` provides). Using `Date.now()` can produce inconsistent results if the system clock changes between events.

### Issue 2: Missing lowercase `timestamp` check

Native events often provide the timestamp in a lowercase `timestamp` field (matching native platform conventions), but the current code only checks for camelCase `timeStamp`. This means valid timestamps from native are being ignored and replaced with the current time.

The affected file is in the React Native renderer's legacy event system:
- `packages/react-native-renderer/src/legacy-events/SyntheticEvent.js`

Look for the `EventInterface` definition and specifically the `timeStamp` getter function. The fix should:
1. Check for both `timeStamp` (camelCase) and `timestamp` (lowercase) properties on the source event
2. Use `performance.now()` as the default fallback when available, with `Date.now()` as a fallback when `performance` is not available
