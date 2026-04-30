# Change browser_run_code argument from code snippet to function

## Problem

The `browser_run_code` MCP tool currently accepts inline code snippets as its `code` parameter. Users provide raw Playwright statements like `await page.getByRole('button', { name: 'Submit' }).click()`, and the tool wraps them in an async IIFE for execution. The `page` object is injected implicitly into the execution scope rather than being passed explicitly.

This design makes the API contract unclear — the `page` object appears magically in scope, the code is evaluated as loose statements, and the tool description tells users to write "code snippets" rather than proper functions. The schema currently describes the parameter as accepting a "Playwright code snippet to run."

## Expected Behavior

The `code` parameter should accept a JavaScript function expression that takes `page` as an argument. For example: `async (page) => { await page.click(...) }`. The tool should invoke this function by passing the page object to it directly, rather than wrapping the code in an IIFE.

- Update the schema description to say something like "A JavaScript function containing Playwright code to execute" — describing the parameter as a function, not a snippet
- Update the schema example to show `async (page) =>` arrow function syntax
- Update the code execution to invoke the user function with `page` instead of wrapping it in an IIFE
- Update the display output (`addCode`) so it shows the invocation wrapping like `await (...)(page);` rather than echoing the raw parameter
- Update the agent definition files across the repository to include the `browser_run_code` tool in the test planner's available tools list

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/runCode.ts` — the MCP tool implementation (uses `vm.createContext` and `vm.runInContext` for code execution)
- Agent definition files in `examples/` and `packages/` directories (specifically the playwright-test-planner agent files)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
