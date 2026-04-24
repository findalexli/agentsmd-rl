# Task: Fix HeatmapChart cells appearing invisible when all data values are equal

## Bug Description

The `getHeatColor` function in `@mantine/charts` produces `NaN` fill colors when all heatmap data values are identical. This makes all heatmap cells invisible.

## Symptom

When a `Heatmap` component receives data where every value is the same (e.g., `{ '2024-06-01': 5, '2024-06-02': 5, '2024-06-03': 5 }`), the cells render with an invisible/transparent fill instead of a visible color.

## Root Cause

The function computes:
```typescript
const percent = (value - min) / (max - min);
const colorIndex = Math.round((colors.length - 1) * percent);
return colors[colorIndex];
```

When `min === max` (all values identical), the denominator `max - min` is `0`, making `percent` equal to `NaN`. `Math.round(NaN * N)` is `NaN`, and `colors[NaN]` is `undefined`.

## Expected Behavior

When `max === min`, the function must still return a valid color string from the `colors` array — it cannot return `undefined`, `NaN`, or any non-string value.

## Target File

`packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts`

The function `getHeatColor({ value, min, max, colors }: GetHeatColorInput)` is used in `HeatmapWeeks.tsx` to compute the `fill` attribute of each `<rect>` element.

## Verification

After fixing the bug:
1. `getHeatColor({ value: 5, min: 5, max: 5, colors: ['1','2','3','4'] })` must return `'4'` (a valid string in the colors array)
2. Normal behavior when `min < max` must still work correctly
3. All existing Heatmap tests must pass

## Test Data

Use this exact input to verify the fix:
```javascript
getHeatColor({ value: 5, min: 5, max: 5, colors: ['1', '2', '3', '4'] })
// Expected: '4'
// Bug behavior: undefined (colors[NaN])
```

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
