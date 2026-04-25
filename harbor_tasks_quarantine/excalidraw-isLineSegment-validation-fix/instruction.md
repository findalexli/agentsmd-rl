# Fix isLineSegment Validation

## Problem

The `isLineSegment` function in the math package has a bug where it doesn't correctly validate all elements of a segment. This allows invalid segments to pass validation, which can lead to unexpected behavior in geometry calculations.

## Location

- **File**: `packages/math/src/segment.ts`
- **Function**: `isLineSegment`

## Expected Behavior

The `isLineSegment` function should validate that:
1. The input is an array
2. The array has exactly 2 elements
3. **Both** elements are valid points (arrays of 2 numbers)

A valid point is: `[number, number]` - an array with exactly 2 numeric elements.

A valid segment is: `[[number, number], [number, number]]` - an array with exactly 2 valid points.

## Symptoms

Invalid segments where the second element is not a valid point (e.g., a string, null, or incorrectly formatted array) may incorrectly pass validation. This could cause issues in downstream geometry operations that expect properly validated segments.

## Notes

- The function is a TypeScript type guard (`segment is LineSegment<Point>`)
- It uses the `isPoint` helper function (also in the math package) to validate individual points
- The packages use Vitest for testing
- Refer to `CLAUDE.md` for development workflow guidelines
