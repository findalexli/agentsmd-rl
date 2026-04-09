# AI Assistant Results Make Page Unresponsive

## Problem

When using the AI Assistant in Supabase Studio with queries returning 1000+ rows, the page becomes unresponsive. Chrome traces show that every keystroke takes approximately 250ms to process, with 70,000+ function calls per long task.

The issue is in the `Results` component used to display SQL query results. Currently, each table cell has its own `ContextMenu_Shadcn_` component instance. Each Radix ContextMenu registers a `keydown` listener on `document` via `useEffect`. With large result sets, this creates thousands of document-level event listeners.

## Expected Behavior

- The AI Assistant should remain responsive when displaying large query results (1000+ rows)
- Typing in the AI Assistant input should not have noticeable lag
- The context menu (right-click on cell) should still work correctly
- Firefox should render the DataGrid properly (currently not rendering in some cases)
- QueryBlock results should not show a double scrollbar

## Files to Look At

- `apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx` — The main Results component that renders query results
- `apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts` — Utility functions for formatting cell values
- `apps/studio/components/ui/QueryBlock/QueryBlock.tsx` — QueryBlock that wraps Results in some contexts

## Additional Context

The Results component:
- Uses `react-data-grid` for table rendering
- Has a right-click context menu on each cell with "Copy cell content" and "View cell content" options
- Uses Radix UI's ContextMenu primitives via `ContextMenu_Shadcn_` imports from the `ui` package
- Currently creates the context menu inside the cell formatter function

Related areas to verify after the fix:
- AI Assistant with large query results (1000+ rows)
- SQL Editor results panel
- QueryBlock in various contexts (Table Editor SQL preview, etc.)
