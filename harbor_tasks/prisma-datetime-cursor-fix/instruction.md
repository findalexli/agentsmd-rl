# Task

Cursor-based pagination on `DateTime` columns is broken for certain database
configurations. When a cursor row is fetched and its `createdAt` value is used
in the next page query, the comparison silently fails and the cursor has no
effect — the query returns the wrong rows.

The bug is in the query variable resolution logic. The scope value for a
`DateTime` cursor is a string (how it arrives from the calling layer), but the
pagination comparison expects a `Date` object. The two values compare as not
equal even when they represent the same point in time.

## Where to look

`packages/client-engine-runtime/src/interpreter/render-query.ts`

The `evaluateArg` function resolves query placeholder variables from the scope.
It handles two kinds of expressions: value placeholders (`isPrismaValuePlaceholder`)
and generator calls (`isPrismaValueGenerator`). The placeholder branch simply
assigns the scope value to `arg` — but it does not account for the case where
the placeholder is typed as `DateTime` and the scope value is a JavaScript
string.

Fix the placeholder branch so that `DateTime` string values are converted to
`Date` objects before being used. Make sure the fix does not affect other
placeholder types.
