# playwright-mcp-expression-evaluate-fix

## Problem

The MCP `browser_evaluate` tool incorrectly wraps JavaScript expressions in `() => (...)` when they happen to contain the characters `=>` anywhere in the string. This causes expressions like `[1,2,3].map(x => x*2)` to be treated as functions and wrapped incorrectly, leading to unexpected evaluation behavior.

The bug is in the `includes('=>')` check which is too naive - it treats any string containing `=>` as a function, including:
- Array expressions: `[1,2,3].map(x => x*2)`
- String literals containing `=>`: `"a => b"`
- Any expression with arrow functions nested inside

## Expected Behavior

The code should properly distinguish between:
1. **Actual functions**: `() => 42`, `x => x*2`, `function foo() { return 1; }`, `async () => 42`
2. **Expressions that may contain `=>`**: `[1,2,3].map(x => x*2)`, `(1+1)`

Functions should be evaluated directly. Non-function expressions should be wrapped in `() => (...)` before evaluation.

## Files to Look At

- `packages/playwright-core/src/tools/backend/evaluate.ts` — The `browser_evaluate` tool implementation
  - Look at the `handle` function
  - The current check `if (!params.function.includes('=>'))` is buggy
  - The fix should use proper function detection (eval + typeof check)

## Related Context

The test file `tests/mcp/evaluate.spec.ts` contains existing tests for the evaluate tool. The PR added a new test case for expressions that was failing before the fix.

## CLAUDE.md Guidance

- Run `npm run build` after making changes
- Run `npm run flint` before committing to check TypeScript compilation
- MCP tests use `npm run ctest-mcp <filter>` for Chromium-only tests

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
