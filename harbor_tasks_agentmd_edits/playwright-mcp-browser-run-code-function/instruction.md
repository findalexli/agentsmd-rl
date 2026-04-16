# Change browser_run_code argument to a function

The `browser_run_code` MCP tool in `packages/playwright/src/mcp/browser/tools/runCode.ts` currently accepts raw Playwright code snippets as a string parameter. This approach has limitations with variable scoping and doesn't provide a clean way to handle the `page` object.

## The Problem

The current implementation injects raw code into an IIFE (Immediately Invoked Function Expression):

```typescript
const result = await (async () => {
  ${params.code};  // Raw code injection
})();
```

This pattern:
- Makes it unclear how the `page` object is accessed
- Can lead to scoping issues with async code
- Is harder to validate and type-check

## What You Need To Do

### 1. Update the Code Implementation

Modify `packages/playwright/src/mcp/browser/tools/runCode.ts` to:

- Change the `codeSchema` description to document that `code` should now be a JavaScript **function** that receives `page` as an argument
- Update the code execution to wrap the function call: `await (${params.code})(page)`
- Remove the old IIFE-based raw code injection pattern

The new format should expect code like:
```javascript
async (page) => { await page.getByRole('button').click(); return await page.title(); }
```

Instead of:
```javascript
await page.getByRole('button').click(); return await page.title();
```

### 2. Update Agent Configurations

Add the `browser_run_code` tool to the agent configuration files. The tool needs to be included in the tools list so that agents know it's available:

- `examples/todomvc/.claude/agents/playwright-test-planner.md` - Add `mcp__playwright-test__browser_run_code` to the tools list
- `examples/todomvc/.github/agents/playwright-test-planner.agent.md` - Add `playwright-test/browser_run_code` to the tools list
- `packages/playwright/src/agents/playwright-test-planner.agent.md` - Add `playwright-test/browser_run_code` to the tools list

### 3. Update Tests

Update `tests/mcp/run-code.spec.ts` to use the new function-based format for the `code` parameter in all test cases.

## Important Notes

- Maintain the existing file structure and exports
- Keep the zod schema validation - only update the description
- The test file uses a custom `toHaveResponse` matcher - update the expected `code` values to match the new wrapped format
- Tool names in different config files use different formats (mcp__ prefix vs playwright-test/ prefix) - follow the existing pattern in each file
