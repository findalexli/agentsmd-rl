# Fix DevTools Profiler Commit Index When Switching Roots

In the React DevTools Profiler, when a user switches between different React roots (e.g., from one rendered component tree to another), the commit index is not reset. This causes the profiler to display stale data or crash if the previous commit index exceeds the bounds of the new root's commit data array.

The issue is in `packages/react-devtools-shared/src/devtools/views/Profiler/useCommitFilteringAndNavigation.js`. The `selectedCommitIndex` state persists across root switches, but the `commitData` array changes when the root changes. There is no mechanism to detect when `commitData` has changed and reset the commit index accordingly.

Fix the hook so that the commit index resets to 0 (or null if empty) whenever the commitData array identity changes, such as when switching between profiled roots.
