# Fix Pivot Table Date Formatting

## Problem

The pivot table chart is showing `0NaN` in column and row headers when using Date/Timestamp data. This happens because `dateFormatters` expect a `number` input but are receiving a `string`, and when the string is non-numeric (like `'Dec. 16 2020'` or `'2024-01-15T00:00:00Z'`), a bare `Number()` cast returns `NaN`.

## Files to Modify

The main file to modify is:
- `superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx`

## Requirements

1. **Add a helper function** `convertToNumberIfNumeric` that:
   - Takes a string value
   - Returns the value as a number IF the string is genuinely numeric
   - Returns the original string if it's not numeric (to avoid NaN)

2. **Use the helper** in both:
   - `renderColHeaderRow` method (column headers)
   - `renderTableRow` method (row headers)

   Both places call `dateFormatters?.[attrName]?.(value)` and should pass the value through `convertToNumberIfNumeric` first.

3. **Follow TypeScript best practices**:
   - Use proper types (string | number return type)
   - Do NOT use `any` types

## What You Should NOT Do

- Do NOT use a bare `Number()` cast on the value (this was the original bug)
- Do NOT convert non-numeric date strings to numbers (they should pass through unchanged)
- Do NOT introduce `any` types

## Testing

The existing test file `superset-frontend/plugins/plugin-chart-pivot-table/test/react-pivottable/tableRenders.test.tsx` contains the test cases. You can run them with:

```bash
cd superset-frontend
npm test -- --testPathPattern=tableRenders.test.tsx
```

The tests verify that:
- Numeric timestamp strings (e.g., `'1700000000000'`) are converted to numbers
- Non-numeric date strings (e.g., `'Dec. 16 2020'`) pass through unchanged
- ISO timestamp strings (e.g., `'2024-01-15T00:00:00Z'`) pass through unchanged
