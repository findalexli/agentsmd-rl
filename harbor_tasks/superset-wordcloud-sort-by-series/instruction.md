# Word cloud secondary sort defeats Druid TopN optimization

## Symptom

The Word Cloud chart's `buildQuery` produces an `ORDER BY` clause that always
appends a secondary sort on the `series` column whenever a `series` is set —
regardless of whether the user asked for it. On Apache Druid, any
multi-column `ORDER BY` disables the native TopN query optimization and
forces a full GroupBy scan over the entire dataset before applying the
`LIMIT`. On high-cardinality dimensions this causes dramatic slowdowns and
query timeouts.

The relevant function is the default export of
`superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/buildQuery.ts`.
Its current logic looks roughly like:

```ts
if (sort_by_metric && metric) {
  orderby.push([metric, false]);   // metric DESC
}
if (series) {
  orderby.push([series, true]);    // series ASC — always added
}
```

The second `if` ignores user intent: a user who only wants a metric-sorted
TopN gets a multi-column sort anyway.

## Required behavior

`buildQuery` must respect an additional form-data field `sort_by_series` (a
boolean) that, together with the existing `sort_by_metric`, gives the user
independent control over sorting:

| `sort_by_metric` | `sort_by_series` | resulting `orderby`                               |
|------------------|------------------|---------------------------------------------------|
| `false`          | `false`          | omitted entirely (no `orderby` field on the query)|
| `true`           | `false`          | `[[metric, false]]`                                |
| `false`          | `true`           | `[[series, true]]`                                 |
| `true`           | `true`           | `[[metric, false], [series, true]]`                |

The truthiness check on `series` itself must remain — only push the series
entry when both `sort_by_series` is truthy AND `series` is set.

The existing rule that `orderby` is only attached to the query at all when
`row_limit` is a non-zero, defined number must be preserved. (The
`shouldApplyOrderBy` guard is already correct; do not change it.)

The function's return shape and its use of `buildQueryContext` from
`@superset-ui/core` must not change.

## Form-data contract

The new control is named exactly `sort_by_series` (matching the existing
`sort_by_metric` style). It is a `CheckboxControl` and lives in the chart's
`controlPanel.tsx`, in the same `Query` section as `sort_by_metric`,
immediately after it.

The new control's default for **new charts** is `false` — the
performance-friendly default. (Existing word-cloud charts in the database
should keep their previous behavior; that is handled separately by a
backfill DB migration that sets `sort_by_series = true` for every existing
`viz_type = "word_cloud"` slice.)

## Fixes #39072

## Code Style Requirements

- TypeScript: do not introduce `any` types; reuse existing types from
  `@superset-ui/core` and the plugin's local `types.ts` where possible.
- Do not introduce new JavaScript (`.js` / `.jsx`) files; new frontend code
  is TypeScript.
- For frontend UI, prefer the wrappers in `@superset-ui/core` over importing
  Ant Design directly.
- Any newly added source file (including a DB migration) must carry the
  standard Apache Software Foundation license header.
- Python additions must use type hints; comments should avoid time-specific
  language ("now", "currently", "today") so they age well.
