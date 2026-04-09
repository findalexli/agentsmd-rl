# Fix Unnecessary Scroll Bars on Charts in Explore View

## Problem

Charts in the Explore view are showing unnecessary scroll bars on initial render, even when they have sufficient space. Resizing the panel by even 1 pixel makes the scroll bars disappear.

## Root Cause

The `useResizeDetectorByObserver` hook in the Explore view has a bug where it observes one element (via `observerRef`) but measures a different element (via `ref`). When the `Split` component resizes the chart container independently of the observed element, the resize isn't detected, causing the chart to render with stale dimensions.

## Files to Modify

1. `superset-frontend/src/explore/components/ExploreChartPanel/useResizeDetectorByObserver.ts`
2. `superset-frontend/src/explore/components/ExploreChartPanel/index.tsx`

## What You Need to Do

The fix requires ensuring the resize detector observes the same element it measures. The `useResizeDetector` hook from `react-resize-detector` supports a `targetRef` option that allows specifying which element to observe.

### Key Requirements

1. In `useResizeDetectorByObserver.ts`:
   - Use the `targetRef` option to observe the same element being measured
   - Remove the separate `observerRef` pattern
   - Continue to use `refreshMode: 'debounce'` with `refreshRate: 300` for performance
   - The hook should return `{ ref, width, height }` (without `observerRef`)

2. In `index.tsx`:
   - Remove all uses of `resizeObserverRef`
   - Continue using `chartPanelRef` for the chart container
   - The `ref` prop on elements should not use the removed observer ref

## Testing

To verify your fix:
1. The hook should no longer return an `observerRef` property
2. The hook should use `targetRef: ref` in its `useResizeDetector` call
3. TypeScript should compile without errors
4. The debounce configuration should remain intact

## Notes

- This is a React hooks bug fix involving the `react-resize-detector` library
- The fix aligns the observation target with the measurement target
- No visual changes are needed, only the hook logic
