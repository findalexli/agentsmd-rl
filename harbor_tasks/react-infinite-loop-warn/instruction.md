# Infinite loop detection should warn for instrumentation-only detections

## Problem

In `packages/react-reconciler/src/ReactFiberWorkLoop.js`, the `throwIfInfiniteUpdateLoopDetected()` function always throws `"Maximum update depth exceeded"` when the nested update count exceeds the limit. However, the `flushSpawnedWork()` function counts nested updates from two distinct sources in a single combined condition:

1. **Traditional detection**: sync lane updates (`includesSomeLane(lanes, UpdateLanes) && includesSomeLane(remainingLanes, SyncUpdateLanes)`)
2. **Instrumentation-gated detection**: render/commit phase spawns (`enableInfiniteRenderLoopDetection && (didIncludeRenderPhaseUpdate || didIncludeCommitPhaseUpdate)`)

Because both sources feed into one `if` branch, `throwIfInfiniteUpdateLoopDetected()` cannot distinguish between them. The instrumentation-gated detections (source #2) are prone to false positives — scenarios where the render would have resolved at a later iteration — and should only produce a warning, not a hard error that interrupts the render and hits an error boundary.

Additionally, the `else` branch in the nested update tracking only resets `nestedUpdateCount` but does not clean up `rootWithNestedUpdates`, which should also be nullified when no nested update was detected.

## Expected Behavior

- When the nested update count is exceeded due to **instrumentation-gated detection** (render/commit phase spawns), `throwIfInfiniteUpdateLoopDetected()` should issue a DEV-only `console.error` warning instead of throwing.
- For **sync-lane detections in render context**, it should also warn instead of throw.
- For **sync-lane detections outside render context**, the hard throw should be preserved.
- When `enableInfiniteRenderLoopDetection` is disabled entirely, the original throw behavior must be preserved.
- The `else` branch should properly reset all nested update tracking state.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberWorkLoop.js` — `flushSpawnedWork()` (where nested update counting happens) and `throwIfInfiniteUpdateLoopDetected()` (where the error/warning decision is made)
