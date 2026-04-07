# Support non-ref selectors in MCP tools and CLI commands

## Problem

The Playwright CLI and MCP tools currently only accept element references (e.g., `e15`, `f1e2`) from page snapshots when targeting elements for interaction. Users cannot pass CSS selectors like `#main > button` or role selectors like `role=button[name=Submit]` directly to CLI commands such as `click`, `fill`, `hover`, etc.

This makes it impossible to interact with elements using standard selectors, which is needed when users explicitly want to target elements by CSS or ARIA role rather than snapshot refs.

## Expected Behavior

1. CLI commands like `click`, `fill`, `hover`, `select`, `check`, `uncheck`, `screenshot`, `evaluate`, and `drag` should accept both snapshot refs AND CSS/role selectors.
2. The system should auto-detect whether the input is a ref pattern (matching `e15`, `f1e2`, etc.) or a selector string, and route accordingly.
3. The underlying MCP tool schemas (`snapshot.ts`, `evaluate.ts`, `form.ts`, `screenshot.ts`, `verify.ts`) should accept an optional `selector` parameter for direct selector-based targeting.
4. The `Tab.refLocator`/`refLocators` methods should handle the new `selector` parameter, creating a `page.locator(selector)` when a selector is provided.
5. The `selector`/`startSelector`/`endSelector` fields should be hidden from the MCP schema (only exposed via CLI), by stripping them in `filteredTools()`.
6. After implementing the code changes, update the project's SKILL.md documentation to explain how to target elements using both refs and selectors, with examples.

## Files to Look At

- `packages/playwright-core/src/cli/daemon/commands.ts` — CLI command declarations; needs a helper to classify ref vs selector and updated arg names
- `packages/playwright-core/src/tools/tab.ts` — `Tab.refLocator`/`refLocators` methods that resolve element locators
- `packages/playwright-core/src/tools/tools.ts` — `filteredTools()` that controls which schema fields are exposed to MCP
- `packages/playwright-core/src/tools/snapshot.ts` — shared `elementSchema` used by click, hover, etc.
- `packages/playwright-core/src/tools/evaluate.ts` — evaluate tool schema
- `packages/playwright-core/src/tools/form.ts` — form fill tool schema
- `packages/playwright-core/src/tools/screenshot.ts` — screenshot tool schema
- `packages/playwright-core/src/tools/verify.ts` — verify list/value tool schemas
- `packages/playwright-core/src/skill/SKILL.md` — CLI skill documentation (should be updated to document new selector support)
