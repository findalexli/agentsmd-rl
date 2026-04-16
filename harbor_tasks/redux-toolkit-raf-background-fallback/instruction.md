# Fix Background Tab Notification Issue in autoBatchEnhancer

## Problem

The default `raf` (requestAnimationFrame) autoBatch strategy in Redux Toolkit doesn't work properly in background tabs. Browsers throttle or completely pause `requestAnimationFrame` callbacks when a tab is not visible, which means batched subscriber notifications from RTK Query fetches never fire until the user returns to the tab.

This causes stale data to remain in the UI while the tab is in the background, even though the fetch has completed.

## Task

Modify `src/autoBatchEnhancer.ts` so that the `raf` autoBatch strategy properly notifies subscribers even when the tab is in the background.

The solution should ensure that:
1. The existing `raf` strategy continues to use `requestAnimationFrame` for efficient batching in foreground tabs
2. A timer-based fallback exists to ensure notifications fire even when `requestAnimationFrame` is throttled or paused
3. The fallback timer should use a 100ms delay to balance responsiveness with performance
4. Exactly one notification occurs per batch (no duplicate notifications when both mechanisms would fire)
5. Foreground tab behavior remains unchanged (notification should still happen at ~16ms via RAF)

## Files to Modify

- `src/autoBatchEnhancer.ts` - Main file containing the autoBatchEnhancer logic

## Testing

After your fix:
- Unit tests should pass: `yarn test src/tests/autoBatchEnhancer.test.ts`
- TypeScript should compile: `yarn tsc --noEmit`
- The 'raf' strategy should properly handle background tab scenarios