# Support non-ref selectors in MCP tools and CLI commands

## Problem

The Playwright CLI and MCP tools currently only accept element references (e.g., `e15`, `f1e2`) from page snapshots when targeting elements for interaction. Users cannot pass CSS selectors like `#main > button` or role selectors like `role=button[name=Submit]` directly to CLI commands such as `click`, `fill`, `hover`, etc.

When a user tries to interact with elements using standard selectors, the system treats them as invalid refs. The system needs to auto-detect whether input is a snapshot ref (strings like `e15`, `f1e2`, `f12e99` matching pattern `^(f\d+)?e\d+$`) or a CSS/role selector, and route accordingly.

## Expected Behavior

1. CLI commands should accept both snapshot refs AND CSS/role selectors for element targeting. Snapshot refs follow the pattern `^(f\d+)?e\d+$` (e.g., `e15`, `f1e2`, `f12e99`). CSS selectors include patterns like `#main > button`. Role selectors include patterns like `role=button[name=Submit]`.

2. The system should classify inputs: strings matching the snapshot ref pattern should be treated as refs; all other strings should be treated as selectors.

3. When classifying input, the behavior should be:
   - Valid refs (matching `^(f\d+)?e\d+$`) should return an object preserving the ref
   - Selectors (all other non-empty strings) should return an object marking it as a selector (ref should be empty string)
   - Undefined/empty input should return an empty object

4. CLI commands (`click`, `dblclick`, `fill`, `hover`, `select`, `check`, `uncheck`, `screenshot`) must use parameter name `target` instead of `ref`, and must invoke a classification helper on that parameter. The helper result should be spread into the tool parameters so refs go to `ref` field and selectors go to `selector` field.

5. The `drag` command must use `startElement` and `endElement` parameter names (not `startRef`/`endRef`), calling the classification helper on both. The helper results should populate `startRef`/`startSelector` and `endRef`/`endSelector` tool parameters.

6. The `Tab.refLocator` and `refLocators` methods in `tab.ts` must accept an optional selector parameter to create a `page.locator(selector)` when a selector is provided. When a selector matches no elements, an error containing the message "does not match any elements" must be thrown.

7. The MCP tool schemas in `snapshot.ts`, `evaluate.ts`, `form.ts`, `screenshot.ts`, and `verify.ts` must include an optional `selector` field declared as `z.string().optional()` with a description mentioning "CSS or role selector".

8. The `filteredTools()` function in `tools.ts` must strip the `selector`, `startSelector`, and `endSelector` fields from tool schemas so they are not exposed via MCP (these should be omitted from the schema).

9. Update `packages/playwright-core/src/skill/SKILL.md` to document the new selector support with:
    - A section about targeting elements
    - Documentation of CSS selectors and role selectors
    - Examples showing `click` with CSS selector (e.g., `click "#main > button"`)
    - Examples showing `click` with role selector (e.g., `click "role=button[name=Submit]"`)
    - Examples showing both ref-based and selector-based interactions

## Files to Look At

- `packages/playwright-core/src/cli/daemon/commands.ts` - CLI command declarations; needs classification helper and updated parameter names
- `packages/playwright-core/src/tools/tab.ts` - `Tab.refLocator`/`refLocators` methods that resolve element locators
- `packages/playwright-core/src/tools/tools.ts` - `filteredTools()` that controls which schema fields are exposed to MCP
- `packages/playwright-core/src/tools/snapshot.ts` - shared element schema used by click, hover, etc.
- `packages/playwright-core/src/tools/evaluate.ts` - evaluate tool schema
- `packages/playwright-core/src/tools/form.ts` - form fill tool schema
- `packages/playwright-core/src/tools/screenshot.ts` - screenshot tool schema
- `packages/playwright-core/src/tools/verify.ts` - verify list/value tool schemas
- `packages/playwright-core/src/skill/SKILL.md` - CLI skill documentation to be updated

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
