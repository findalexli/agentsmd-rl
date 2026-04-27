# Preserve dynamic group-by column order in AgGrid Table V2

The Apache Superset checkout at `/workspace/superset` contains a frontend
bug in the AgGrid `Table V2` chart plugin
(`superset-frontend/plugins/plugin-chart-ag-grid-table`). When a dashboard
filter or display control changes the chart's grouped dimension at
runtime — i.e. the chart's column **set** changes, not just column
widths — the table renders the new dimension in the wrong place.

## Reproducing the symptom

1. AgGrid Table V2 chart with one grouped dimension `D_old` and metrics
   `M1`, `M2`. The chart is added to a dashboard; the user reorders or
   resizes columns, and that final column state is persisted as
   `chartState.columnState` (an array of `{ colId, ... }` entries that
   remembers each column's saved position, width, sort, etc.).
2. A `Dynamic group by` display control swaps the grouped dimension to
   `D_new`. The backend correctly returns rows shaped
   `[D_new, M1, M2]`, and the frontend rebuilds `colDefsFromProps` in
   that order.
3. **Expected:** the table renders `D_new` as the first column.
4. **Actual:** the table renders `[M1, M2, D_new]` — the new dimension
   gets appended to the end.

The cause sits in `AgGridTable/index.tsx`'s `onGridReady` handler: when
`chartState.columnState` exists, the handler unconditionally calls
AG Grid's `params.api.applyColumnState({ state: chartState.columnState,
applyOrder: true })`. With `applyOrder: true`, AG Grid honors the saved
order verbatim — but the saved order references a `colId` (`D_old`) that
no longer exists in the current column set, so AG Grid keeps the metric
columns where the saved state pinned them and the new dimension is
appended at the tail.

## What needs to change

This is a frontend rendering fix only. **Do not** touch SQL building,
sorting logic, row limits, or query-result handling.

### 1. Add a new utility module

Create
`superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.ts`.

The module must export:

- A **named** export `getLeafColumnIds(colDefs)` returning `string[]`.
  - Walk `colDefs` left-to-right and emit each leaf's `field`.
  - When an entry is a column **group** (has a non-empty `children`
    array), recurse into it so the children's fields appear inline,
    preserving visual order.
  - Treat entries with an empty/missing `children` array and a
    non-string `field` as having no leaf id (skip them).
  - Example: input
    `[{field:'A'}, {headerName:'g', children:[{field:'B'},{field:'C'}]}, {field:'D'}]`
    → `['A','B','C','D']`.

- A **default** export `reconcileColumnState(savedColumnState, colDefs)`
  that returns either `null` or an object
  `{ applyOrder: boolean, columnState: ColumnState[] }`. Use the
  type `ColDef` and `ColumnState` from
  `@superset-ui/core/components/ThemedAgGridReact` (type-only imports).

  Contract:
  1. If `savedColumnState` is missing, not an array, or empty → `null`.
  2. Compute the current leaf column ids from `colDefs` via
     `getLeafColumnIds`.
  3. Build a *filtered* saved state that drops every entry whose
     `colId` is not a string or is not present in the current leaf set.
     If filtering empties the array → `null`.
  4. The returned `columnState` is exactly that filtered array, in the
     **saved order**, with every other `ColumnState` field preserved
     unchanged (`width`, `sort`, `pinned`, …).
  5. `applyOrder` is `true` **iff the filtered saved colId set equals
     the current leaf id set** (same size and same membership). If the
     current set has any column that isn't in the saved state — for
     example because a dynamic group-by swap added a new dimension —
     `applyOrder` must be `false` so AG Grid falls back to the current
     query order.

### 2. Route AgGrid Table V2 through the helper

In `superset-frontend/plugins/plugin-chart-ag-grid-table/src/AgGridTable/index.tsx`:

- Import the new default export from `../utils/reconcileColumnState`.
- In the `onGridReady` handler's `chartState?.columnState` branch,
  replace the unconditional
  `params.api.applyColumnState?.({ state: chartState.columnState, applyOrder: true })`
  call. Instead, call the helper with the saved state and
  `colDefsFromProps`, and only apply column state when the helper
  returns a non-null result. The `state` and `applyOrder` arguments to
  `applyColumnState` must come from the helper's return value.
- The surrounding `try/catch` that silently swallows restoration errors
  stays.

### 3. Add a test file alongside the helper

Create
`superset-frontend/plugins/plugin-chart-ag-grid-table/src/utils/reconcileColumnState.test.ts`
covering at least:

- `getLeafColumnIds` flattens grouped column defs in visual order.
- `reconcileColumnState` preserves saved order when the current column
  set is unchanged.
- `reconcileColumnState` drops stale order when a dynamic group by swaps
  the dimension column.

## Code Style Requirements

This repo's `AGENTS.md` / `CLAUDE.md` / `.cursor/rules/dev-standard.mdc`
apply to every file you touch:

- **Apache License Headers.** Every new source file (`.ts` and
  `.test.ts`) must begin with the standard ASF license header
  ("Licensed to the Apache Software Foundation … Apache License,
  Version 2.0 …"). Match the format used by other new files in this
  plugin.
- **No `any` types.** Don't introduce `: any`, `as any`, or `<any>`.
  Reuse `ColDef` / `ColumnState` from
  `@superset-ui/core/components/ThemedAgGridReact` and define a small
  local type if you need to model a column-group def with `children`.
- **Use `test()` instead of `describe()`** in the new test file
  (the project follows the "avoid nesting when testing" pattern).
- **Timeless comments.** Don't write code comments that use
  time-specific words like "now", "currently", or "today".
