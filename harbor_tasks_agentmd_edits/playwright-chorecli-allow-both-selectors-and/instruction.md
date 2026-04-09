# Allow both selectors and Playwright locators in CLI element targeting

## Problem

The Playwright CLI currently accepts CSS selectors and old-style `role=button[name=Submit]` syntax when targeting elements (via `click`, `fill`, `hover`, etc.). However, it does not support modern Playwright locator strings like `getByRole('button', { name: 'Submit' })` or `getByTestId('my-id')`.

When a user passes a locator string such as `getByRole('button')` to `playwright-cli click`, the CLI tries to use it as a raw selector, which fails or produces unexpected results. The `locatorOrSelectorAsSelector` utility already exists in `packages/playwright-core/src/utils/isomorphic/locatorParser.ts` and can convert locator strings to internal selectors, but the tab's element resolution code in `packages/playwright-core/src/tools/backend/tab.ts` does not use it.

## Expected Behavior

1. The `refLocators` method in `tab.ts` should convert the incoming selector through `locatorOrSelectorAsSelector` before creating a locator, so that both CSS selectors and Playwright locator strings work.
2. The element existence check should use `page.$()` (returns a handle or null) rather than `locator.isVisible()` for more reliable detection.
3. After fixing the code, update the CLI's SKILL.md documentation (`packages/playwright-core/src/tools/cli-client/skill/SKILL.md`) to reflect that Playwright locator syntax is now supported alongside CSS selectors. Replace the old `role=button[name=Submit]` examples with modern locator syntax like `getByRole()` and `getByTestId()`.

## Files to Look At

- `packages/playwright-core/src/tools/backend/tab.ts` — `refLocators()` method that resolves element references and selectors
- `packages/playwright-core/src/utils/isomorphic/locatorParser.ts` — contains `locatorOrSelectorAsSelector` utility
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — CLI skill documentation, "Targeting elements" section
