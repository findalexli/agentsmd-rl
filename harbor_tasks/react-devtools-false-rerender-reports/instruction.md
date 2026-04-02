# Bug Report: React DevTools Profiler Reports False Re-renders for Components Behind Filtered Fibers

## Problem

When using React DevTools Profiler, components are incorrectly reported as having re-rendered even when they did not. This happens specifically when a component's parent fiber is filtered out of the DevTools tree (e.g., host components like `<div>` or keyless `Fragment` wrappers). During a profiling session, if a sibling component triggers a state update, unrelated components that share a filtered parent are falsely marked with `didRender: true` in the flamegraph chart data.

## Expected Behavior

When profiling a React application, the flamegraph should accurately reflect which components actually re-rendered during a commit. A component that bailed out (did not re-render) should show `didRender: false`, regardless of whether its parent fiber is filtered from the DevTools component tree.

## Actual Behavior

Components behind filtered fibers (such as host DOM elements or Fragments) are incorrectly reported as re-rendered in profiling data when a sibling component updates. For example, a static `<Greeting>` component nested inside a filtered `<div>` is marked as re-rendered when only a sibling `<Count>` component updated its state.

## Files to Look At

- `packages/react-devtools-shared/src/backend/fiber/renderer.js`
- `packages/react-devtools-shared/src/__tests__/profilingCharts-test.js`
