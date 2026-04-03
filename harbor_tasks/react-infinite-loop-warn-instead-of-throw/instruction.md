# Change Infinite Loop Detection to Warn Instead of Throw

React's infinite render loop detection in `packages/react-reconciler/src/ReactFiberWorkLoop.js` currently throws an error for all cases of detected infinite updates. However, there are two distinct categories:

1. **Sync lane nested updates**: The render finished with update lanes remaining in sync lanes. This is the traditional detection path.
2. **Phase-spawned updates**: Updates spawned during the render or commit phase, detected by the `enableInfiniteRenderLoopDetection` feature flag instrumentation.

For case 2 (instrumentation-gated detection), throwing an error is too aggressive. Since these are detected via newer instrumentation that may have false positives, they should issue a `console.error` warning in development mode instead of throwing.

The fix should:
- Track which kind of nested update was detected (sync lane vs phase spawn)
- For sync lane updates in render context: warn via console.error instead of throwing
- For phase-spawned updates: always warn via console.error
- Keep the throwing behavior for sync lane updates outside render context
