# Performance Issue: SQL Editor Results Component

## Problem

In the Supabase Studio SQL Editor, executing queries that return 1000+ rows causes the page to become severely unresponsive. Chrome DevTools traces show each keystroke takes approximately 250ms to process, with over 70,000 function calls per long task.

The root cause is that the Results component at `apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx` renders a separate `ContextMenu_Shadcn_` component inside every cell's `renderCell` callback. With a large result set, this creates thousands of document-level keydown listeners, degrading keyboard responsiveness.

A secondary issue exists in `apps/studio/components/ui/QueryBlock/QueryBlock.tsx`, where the container wrapping the Results component uses `overflow-auto`, causing double scrollbar problems in Firefox.

## Task

Fix the performance problem and the layout issue described above. The solution must satisfy all of the acceptance criteria below.

## Acceptance Criteria

### 1. Single Shared Context Menu in Results.tsx

The Results component (`apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx`) must be refactored so that:

- There is exactly **one** `<ContextMenu_Shadcn_>` element rendered at the component level, outside of `renderCell`. The `renderCell` callback must **not** contain any `ContextMenu_Shadcn_` or `ContextMenu_Shadcn` elements.
- The component uses React refs to manage shared state for the context menu:
  - A ref to store the column and value of the cell that was right-clicked
  - A ref for a hidden trigger element that is repositioned to the cursor location on right-click
- A callback handler coordinates opening the shared context menu at the cursor position.
- The `columns` array is memoized.
- Cell values are formatted for display using `formatCellValue` (imported from `./Results.utils`).
- Clipboard values are formatted using `formatClipboardValue` (also imported from `./Results.utils`).

### 2. Utility Functions in Results.utils.ts

The file `apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts` must export these functions (in addition to the already-existing `formatResults`, `convertResultsToCSV`, `convertResultsToMarkdown`, `convertResultsToJSON`, and `getResultsHeaders`):

- **`formatClipboardValue`** — formats a value for clipboard operations:
  - Returns empty string `''` for `null`
  - Returns `JSON.stringify(value)` for objects and arrays
  - Returns the string representation for primitives

- **`formatCellValue`** — formats a value for cell display:
  - Returns the string `'NULL'` for `null`
  - Returns the value as-is for strings
  - Returns `JSON.stringify(value)` for all other types

### 3. QueryBlock Layout Fix

In `apps/studio/components/ui/QueryBlock/QueryBlock.tsx`:

- The component must use the CSS class `flex-1`.
- The `<div>` container that wraps `<Results rows={results}>` must use `flex flex-col` and `max-h-64` CSS classes (replacing the previous `overflow-auto` approach) to fix the double-scrollbar issue in Firefox.

### 4. Test Files

Create the following test files:

- **`apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.test.ts`** — basic test file for the utility functions.

- **`apps/studio/tests/components/SQLEditor/Results.utils.test.ts`** — must contain `describe('formatClipboardValue'` and/or `describe('formatCellValue'` blocks testing the utility functions' behavior.

- **`apps/studio/tests/components/SQLEditor/Results.test.tsx`** — must contain test cases verifying that: (1) only a single context menu is rendered regardless of how many rows are displayed (tracking how many times `ContextMenu_Shadcn_` mounts, asserting exactly one instance exists), and (2) an empty state message is shown when no rows are provided (the empty state displays the text `Success. No rows returned`).

### 5. Code Formatting

All modified and new files must pass `pnpm run test:prettier`.