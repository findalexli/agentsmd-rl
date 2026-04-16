Update the `browser_run_code` tool to accept a JavaScript function expression instead of raw code snippets.

## Background

Currently, the `browser_run_code` tool's `code` parameter accepts raw JavaScript code that gets directly injected into an execution context. This has security and usability issues - users should instead provide a function expression that receives the `page` object as an argument.

## Requirements

### 1. Update `packages/playwright/src/mcp/browser/tools/runCode.ts`

**Parameter documentation changes:**

The `code` parameter description must be updated to document that it accepts a JavaScript function expression. The description must include:
- The example pattern `async (page) =>`
- Text stating the function receives "a single argument, page" OR "page, which you can use"
- An example showing how to use the `page` argument for browser interactions (e.g., `await page.getByRole('button').click()`)

**Execution logic changes:**

The current implementation directly injects the raw code string. This should be changed to:
- Invoke the provided code as a function call with the `page` object
- The pattern `(${params.code})(page)` must appear at least twice in the file (in both the code display and the execution logic)
- The file must NOT contain bare `${params.code}` followed by a semicolon (the old direct injection pattern)

### 2. Add `browser_run_code` tool to agent definition files

Add the `browser_run_code` tool to three agent definition files in alphabetical order between `browser_press_key` and `browser_select_option`:

1. **File:** `examples/todomvc/.claude/agents/playwright-test-planner.md`
   - **Tool format:** `mcp__playwright-test__browser_run_code` (comma-separated list)
   - **Position:** After `mcp__playwright-test__browser_press_key`, before `mcp__playwright-test__browser_select_option`

2. **File:** `examples/todomvc/.github/agents/playwright-test-planner.agent.md`
   - **Tool format:** `playwright-test/browser_run_code` (YAML list)
   - **Position:** After `playwright-test/browser_press_key`, before `playwright-test/browser_select_option`

3. **File:** `packages/playwright/src/agents/playwright-test-planner.agent.md`
   - **Tool format:** `playwright-test/browser_run_code` (YAML list)
   - **Position:** After `playwright-test/browser_press_key`, before `playwright-test/browser_select_option`

### 3. Verify the changes

The tests in `tests/mcp/run-code.spec.ts` exercise the tool functionality and should pass after your changes.
