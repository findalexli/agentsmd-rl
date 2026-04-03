# CLI click/hover/fill commands only accept raw selectors, not Playwright locators

## Problem

The `playwright-cli` tool's element targeting commands (`click`, `hover`, `fill`, etc.) only accept CSS selectors and the internal `role=...` selector syntax. Users cannot pass Playwright locator expressions like `getByRole('button', { name: 'Submit' })` or `getByTestId('my-element')` — these are silently treated as CSS selectors and fail to match anything.

The CLI should accept both raw CSS selectors **and** Playwright locator expressions interchangeably, using the existing `locatorOrSelectorAsSelector` utility from `locatorParser` to convert locator strings into the internal selector format.

## Expected Behavior

When a user passes a Playwright locator expression (e.g., `getByRole(...)`, `getByTestId(...)`) to a CLI command, it should be recognized and converted to a valid selector before querying the page. CSS selectors should continue to work as before.

The error message when no element matches should also be improved — currently it says `Selector <value> does not match...` which is misleading when the input is a locator expression.

## Files to Look At

- `packages/playwright-core/src/tools/backend/tab.ts` — the `resolveElements` method handles element resolution for CLI commands
- `packages/playwright-core/src/utils/isomorphic/locatorParser.ts` — contains `locatorOrSelectorAsSelector` which can convert both selectors and locator strings

After making the code change, update the CLI skill documentation to reflect that locator expressions are now supported in element targeting. The skill documentation should show examples of the new locator syntax.

- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — documents how to target elements with `playwright-cli`
