# AI Assistant Results Performance Fix

## Problem

When using the AI Assistant in Supabase Studio with queries returning 1000+ rows, the page becomes unresponsive. Chrome traces show that every keystroke takes approximately 250ms to process, with 70,000+ function calls per long task.

The performance bottleneck is in the Results component and QueryBlock component used to display SQL query results.

## Files to Modify

- `apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx`
- `apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts`
- `apps/studio/components/ui/QueryBlock/QueryBlock.tsx`

## Requirements

### Results.tsx

The Results component must be refactored with the following:

- Import `useCallback`, `useMemo`, and `useRef` from React (in addition to existing imports)
- Import `formatCellValue` and `formatClipboardValue` from `./Results.utils`
- Define a ref named `contextMenuCellRef` (typed as an object with `column` and `value` fields, or null)
- Define a ref named `triggerRef` (typed as `HTMLDivElement`)
- Define a function named `handleContextMenu` wrapped in `useCallback`
- Wrap the `columns` definition in `useMemo`
- Render a single `<ContextMenu_Shadcn_>` component at the component level (outside `renderCell`)
- The `renderCell` callback must NOT contain `ContextMenu_Shadcn_` or `ContextMenu_Shadcn`
- The renderCell function should call `formatCellValue` to display cell values

### Results.utils.ts

The utility file must export the following functions:

- `formatClipboardValue` — formats values for clipboard: returns empty string for null, `JSON.stringify` for objects/arrays, string representation for primitives
- `formatCellValue` — formats values for display: returns `'NULL'` for null, value as-is for strings, `JSON.stringify` for others
- `formatResults` (already exists, keep it)
- `convertResultsToCSV` (already exists, keep it)
- `convertResultsToMarkdown` (already exists, keep it)
- `convertResultsToJSON` (already exists, keep it)
- `getResultsHeaders` (already exists, keep it)

### QueryBlock.tsx

- The component must include the CSS class `flex-1`
- The container `<div>` wrapping `<Results rows={results}>` must have both CSS classes `flex flex-col` and `max-h-64` on the same line

### Test Files

Create the following test files:

- `apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.test.ts`
- `apps/studio/tests/components/SQLEditor/Results.utils.test.ts` — must contain `describe('formatClipboardValue'` and/or `describe('formatCellValue'`
- `apps/studio/tests/components/SQLEditor/Results.test.tsx` — must test that only one context menu is rendered regardless of row count, using a variable named `contextMenuMountCount` with the assertion `expect(contextMenuMountCount).toBe(1)`

### Formatting

- All code must pass `pnpm run test:prettier`
