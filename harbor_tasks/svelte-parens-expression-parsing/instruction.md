# Fix parenthesized template expressions with comments

## Problem

The Svelte template parser fails to parse expressions where an opening parenthesis appears before a comment inside a template expression. For example, this valid Svelte template causes a parse error:

```svelte
{(/**/ 42)}
```

Similarly, any template expression where a `(` precedes a comment — such as `{(/* comment */ "hello")}` or `{(/**/ someVar)}` — will fail to parse at compile time.

## Expected Behavior

Parenthesized expressions with comments inside them should parse correctly, producing the expected AST nodes (e.g., the expression `{(/**/ 42)}` should yield a numeric literal `42`).

## Files to Look At

- `packages/svelte/src/compiler/phases/1-parse/read/expression.js` — the `read_expression` function that reads template expressions and handles parentheses
- `packages/svelte/src/compiler/phases/1-parse/acorn.js` — the `parse_expression_at` wrapper around acorn's parser
- `packages/svelte/src/compiler/phases/1-parse/read/context.js` — pattern/context reading that also calls `parse_expression_at`
- `packages/svelte/src/compiler/phases/1-parse/state/tag.js` — tag parsing that calls `parse_expression_at`
