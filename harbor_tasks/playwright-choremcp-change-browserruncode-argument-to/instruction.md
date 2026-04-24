# Change browser_run_code argument from code snippet to function

## Problem

The `browser_run_code` MCP tool currently accepts inline code snippets as its `code` parameter. Users provide raw Playwright statements like `await page.getByRole('button', { name: 'Submit' }).click()`, and the tool wraps them in an async IIFE for execution. The `page` object is injected implicitly into the execution scope rather than being passed explicitly.

This design makes the API contract unclear — the `page` object appears magically in scope, the code is evaluated as loose statements, and the tool description tells users to write "code snippets" rather than proper functions.

## Expected Behavior

The `code` parameter should accept a JavaScript function expression that takes `page` as an argument. For example: `async (page) => { await page.click(...) }`. The tool should invoke this function by passing the page object to it directly, rather than wrapping the code in an IIFE.

- Update the schema description and example to reflect function-based API
- Update the code execution to invoke the user function with `page` instead of wrapping it in an IIFE
- Update the display output (`addCode`) to show the invocation format
- Update the agent definition files across the repository to include this tool in the test planner's available tools

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/runCode.ts` — the MCP tool implementation
- Agent definition files in `examples/` and `packages/` directories

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
