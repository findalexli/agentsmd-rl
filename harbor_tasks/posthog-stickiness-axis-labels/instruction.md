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

## Files to Look At

- `frontend/src/lib/charts/utils/dates.ts` — contains `createXAxisTickCallback` which produces the x-axis tick formatter. Currently has no mechanism to prefix numeric (non-date) tick values.
- `frontend/src/scenes/insights/views/LineGraph/LineGraph.tsx` — the line graph component that calls `createXAxisTickCallback`. This is where stickiness-specific behavior needs to be wired up.
