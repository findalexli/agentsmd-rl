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

## Implementation Requirements

The following specific names and patterns must be implemented:

### Ref Classification Function

A helper function must be added to `commands.ts` that classifies an input string as either a snapshot ref or a CSS/role selector:

- **Function name**: `asRef`
- **Signature**: `function asRef(refOrSelector: string | undefined): { ref?: string, selector?: string }`
- **Pattern matching**: Refs follow the pattern `/^(f\d+)?e\d+$/` (e.g., `e15`, `f1e2`, `f12e99` are valid refs)
- **Return values**:
  - For valid refs: return `{ ref: refOrSelector }` (e.g., `asRef('e15')` returns `{ ref: 'e15' }`)
  - For selectors: return `{ ref: '', selector: refOrSelector }` (e.g., `asRef('#main')` returns `{ ref: '', selector: '#main' }`)
  - For undefined: return `{}`

### CLI Command Parameter Names

- Commands `click`, `dblclick`, `fill`, `hover`, `select`, `check`, `uncheck`, and `screenshot` must use the parameter name `target` (not `ref`) in their `z.object` argument schema
- At least 7 commands must use `target: z.string()` in their argument schema
- The `drag` command must use `startElement` and `endElement` (not `startRef`/`endRef`)

### Tab.refLocator / refLocators

The `refLocator` and `refLocators` methods in `tab.ts` must accept an optional `selector` parameter:
- Signature: `selector?: string` in the params object
- When `selector` is provided, create a locator using `page.locator(param.selector)`
- When the selector matches no elements, throw an error containing the message: `"does not match any elements"`

### MCP Tool Schemas

Each of these files must include an optional `selector` field in its input schema:
- `snapshot.ts` (elementSchema)
- `evaluate.ts`
- `screenshot.ts`
- `verify.ts`
- `form.ts`

The `selector` field must be declared as `z.string().optional()`.

### filteredTools() in tools.ts

The `filteredTools()` function must strip the `selector`, `startSelector`, and `endSelector` fields from tool schemas so they are not exposed via MCP. This is done using `.omit()` with `{ selector: true, startSelector: true, endSelector: true }`.

### SKILL.md Documentation

The `packages/playwright-core/src/skill/SKILL.md` file must be updated with:
- A section about targeting elements
- Documentation of CSS selectors and role selectors
- Examples showing `click` with CSS selector (e.g., `click "#main > button"`)
- Examples showing `click` with role selector (e.g., `click "role=button[name=Submit]"`)
- Examples showing both ref-based and selector-based interactions

## Files to Look At

- `packages/playwright-core/src/cli/daemon/commands.ts` — CLI command declarations; needs the ref-classification helper function (`asRef`) and updated parameter names (`target`, `startElement`, `endElement`)
- `packages/playwright-core/src/tools/tab.ts` — `Tab.refLocator`/`refLocators` methods that resolve element locators; needs to handle the `selector` parameter
- `packages/playwright-core/src/tools/tools.ts` — `filteredTools()` that controls which schema fields are exposed to MCP; needs to strip selector fields
- `packages/playwright-core/src/tools/snapshot.ts` — shared `elementSchema` used by click, hover, etc.; needs optional `selector` field
- `packages/playwright-core/src/tools/evaluate.ts` — evaluate tool schema; needs optional `selector` field
- `packages/playwright-core/src/tools/form.ts` — form fill tool schema; needs optional `selector` field
- `packages/playwright-core/src/tools/screenshot.ts` — screenshot tool schema; needs optional `selector` field
- `packages/playwright-core/src/tools/verify.ts` — verify list/value tool schemas; needs optional `selector` field
- `packages/playwright-core/src/skill/SKILL.md` — CLI skill documentation (must be updated to document new selector support)
