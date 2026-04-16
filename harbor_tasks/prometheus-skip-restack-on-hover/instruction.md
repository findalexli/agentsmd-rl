# Fix UI Performance: Skip Recomputing Stacked Chart Data on Hover

## Problem

The Prometheus query UI uses uPlot for rendering stacked series charts. When users hover over or focus on chart series, the chart unnecessarily recomputes all stacked data via the `setSeries` hook. This causes performance issues because each hover/focus event triggers expensive `stack()`, `delBand()`, `addBand()`, and `setData()` operations.

uPlot's `setSeries` hook callback receives information about **why** the hook is being called. When the hook is invoked for a visibility toggle, the expensive restacking should happen. When it's invoked for hover/focus only, restacking should be skipped.

## Your Task

Modify `web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts` to fix this performance issue:

1. Examine what additional parameters uPlot passes to the `setSeries` hook callback (beyond the series index)
2. Use this information to distinguish between hover/focus events and visibility toggle events
3. Restack only when a series visibility toggle occurs, not on every hook invocation
4. Update the comment above the hook to reflect the new behavior

## Key File

- `web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts` - Look for the `setStackedOpts` function and its `setSeries` hook

## Expected Behavior After Fix

- Hovering over chart series should NOT trigger expensive restacking operations
- Toggling series visibility (show/hide) should still correctly restack the data
- TypeScript should compile without errors