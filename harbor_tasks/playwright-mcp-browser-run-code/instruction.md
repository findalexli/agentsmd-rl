Update the `browser_run_code` tool to accept a JavaScript function expression instead of raw code snippets.

## Background

Currently, the `browser_run_code` tool's `code` parameter accepts raw JavaScript code that gets directly injected into an execution context. This has security and usability issues - users should instead provide a function expression that receives the `page` object as an argument.

## Requirements

### 1. Update `packages/playwright/src/mcp/browser/tools/runCode.ts`

**Parameter documentation changes:**

The `code` parameter's schema description should be updated to document the new function-based API. It should explain that the parameter accepts a JavaScript function expression that receives the Playwright `page` object for browser interactions, and include a usage example showing the expected format.

**Execution logic changes:**

The current implementation directly injects the raw `code` string as statements inside an async IIFE wrapper. This should be changed so that the provided code is treated as a function expression and invoked with the `page` object as its argument. Both the code display (via `addCode`) and the actual `vm` execution should call the user's code as a function rather than injecting it as raw statements.

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
