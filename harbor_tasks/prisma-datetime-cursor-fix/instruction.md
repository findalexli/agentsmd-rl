# Task

Cursor-based pagination on `DateTime` columns silently returns the wrong rows
when the cursor is applied. The query executes without error but the cursor has
no effect — rows that should be excluded by the cursor boundary are still
returned.

The root cause: a string-to-date conversion is missing in the query variable
resolution path for `DateTime` typed placeholders. The scope value arrives as a
JavaScript string, but the database comparison expects a `Date` object. The two
compare as not equal even when they represent the same date.

When a placeholder passed to `evaluateArg()` has the shape:
```typescript
{
  prisma__type: 'param',
  prisma__value: { name: string, type: 'DateTime' }
}
```
and the corresponding scope entry is a string such as `'2025-01-03'`, the
function must return a `Date` instance rather than the bare string.

**Note:** The fix must apply only when `type` is `"DateTime"` — other
placeholder types (e.g., `"String"`, `"Int"`, `"Float"`, `"Boolean"`,
`"Json"`) must remain unaffected and return their scope value unchanged.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
