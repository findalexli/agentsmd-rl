# Stickiness insight chart x-axis labels lost interval context

## Problem

Stickiness insights in the line graph show plain numeric x-axis labels like `1`, `2`, `3` instead of interval-prefixed labels like `Day 1`, `Week 2`, `Month 3`. This makes it hard for users to understand what the numbers represent at a glance.

The regression affects all stickiness charts regardless of which interval (day, week, month) is selected. Non-stickiness insights with date-based x-axes are unaffected.

## Expected Behavior

When viewing a stickiness insight:
- With day interval: labels should read `Day 1`, `Day 2`, `Day 3`, ...
- With week interval: labels should read `Week 1`, `Week 2`, `Week 3`, ...
- With month interval: labels should read `Month 1`, `Month 2`, `Month 3`, ...

Non-stickiness insights should continue to display date-formatted labels as before.

## Implementation Requirements

### dates.ts

The `createXAxisTickCallback` function in `frontend/src/lib/charts/utils/dates.ts` must accept a new parameter named exactly `numericTickPrefix` that:
- When provided, formats numeric tick values as `{prefix} {value}` (e.g., `Day 1`, `Week 2`)
- When not provided (undefined), continues returning plain numeric strings for backward compatibility

The file must import dayjs from `lib/dayjs` (not directly from the `dayjs` package).

### LineGraph.tsx

The line graph component in `frontend/src/scenes/insights/views/LineGraph/LineGraph.tsx` must:
- Access a value named exactly `isStickiness` from `insightVizDataLogic` to determine when a chart represents stickiness data
- Pass a property named exactly `numericTickPrefix` to `createXAxisTickCallback` only when `isStickiness` is true
- The prefix should be derived from the current interval: capitalize the interval name (`day` → `Day`, `week` → `Week`, `month` → `Month`)
