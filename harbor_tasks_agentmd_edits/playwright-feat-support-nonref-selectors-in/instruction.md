# Support Non-Ref Selectors in CLI and MCP Tools

## Problem

The Playwright CLI (`playwright-cli`) and MCP tools currently only support targeting page elements by their snapshot reference (e.g., `e5`, `f1e2`). Users must first take a snapshot to obtain refs before interacting with elements. There is no way to use CSS selectors (`#main > button`), role selectors (`role=button[name=Submit]`), or chained selectors (`#footer >> role=button`) directly.

This limitation is frustrating when the user already knows the exact selector they want to target, or when they want to use selectors that are more stable than snapshot refs.

## Expected Behavior

CLI commands and MCP tools that target elements (click, fill, hover, select, check, uncheck, evaluate, screenshot, drag, etc.) should accept **both** element refs and CSS/role selectors:

- Element refs like `e5` or `f1e2` should continue to work as before
- CSS selectors like `button`, `#main > .submit` should be accepted
- Role selectors like `role=button[name=Submit]` should be accepted
- Chained selectors like `#footer >> role=button` should be accepted
- Invalid selectors should produce a clear error message

The system should auto-detect whether the input is a ref or a selector based on the format.

Note that while MCP tools should internally support selectors, the `selector` parameter should **not** be exposed in the MCP tool schemas — selectors should only be available through the CLI interface and skill system.

After implementing the code changes, update the relevant skill documentation to explain the new targeting capabilities so that agents know how to use selectors.

## Files to Look At

- `packages/playwright-core/src/cli/daemon/commands.ts` — CLI command definitions with arg schemas
- `packages/playwright-core/src/tools/tab.ts` — `refLocator`/`refLocators` methods that resolve element targets
- `packages/playwright-core/src/tools/snapshot.ts` — shared `elementSchema` used by click, hover, etc.
- `packages/playwright-core/src/tools/tools.ts` — `filteredTools` function that prepares MCP tool schemas
- `packages/playwright-core/src/tools/evaluate.ts`, `form.ts`, `screenshot.ts`, `verify.ts` — individual tool implementations
- `packages/playwright-core/src/skill/SKILL.md` — skill documentation for `playwright-cli`
