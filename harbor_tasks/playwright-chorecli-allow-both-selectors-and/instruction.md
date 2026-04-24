# Allow both selectors and Playwright locators in CLI element targeting

## Problem

The Playwright CLI currently accepts CSS selectors and old-style `role=button[name=Submit]` syntax when targeting elements (via `click`, `fill`, `hover`, etc.). However, it does not support modern Playwright locator strings like `getByRole('button', { name: 'Submit' })` or `getByTestId('my-id')`.

When a user passes a locator string such as `getByRole('button')` to `playwright-cli click`, the CLI tries to use it as a raw CSS selector, which fails or produces unexpected results. The codebase already contains a utility module for converting locator strings to internal selectors at `packages/playwright-core/src/utils/isomorphic/locatorParser.ts`, but the backend tab code does not use it.

Additionally, when a selector doesn't match any elements, the current error message uses the format:
```
Selector ${param.selector} does not match any elements.
```
The selector value should be quoted for clarity:
```
"${param.selector}" does not match any elements.
```

## Expected Behavior

1. The element resolution code in `tab.ts` should leverage the locator parser utilities from `locatorParser.ts` to convert incoming selector strings — both CSS selectors and Playwright locator syntax — into internal selectors before use. The parser function in that module requires the language identifier, the raw selector string, and the `testIdAttribute` configuration value as arguments.

2. Element existence should be checked using `page.$()` (Playwright's query selector method that returns an element handle or null) for reliable detection with both selector types.

3. When an element is not found, the error message must use the format: `"${param.selector}" does not match any elements.` — with the selector value surrounded by double quotes and without a "Selector" prefix.

4. After fixing the code, update the CLI documentation (`packages/playwright-core/src/tools/cli-client/skill/SKILL.md`) to reflect that Playwright locator syntax is now supported alongside CSS selectors. The "Targeting elements" section should:
   - Reference "Playwright locators" in its description
   - Include a `getByRole` example demonstrating role-based element targeting (e.g., targeting a button)
   - Include a `getByTestId` example
   - Preserve existing ref-based and CSS selector examples

## Files to Look At

- `packages/playwright-core/src/tools/backend/tab.ts` — element resolution code that handles selectors
- `packages/playwright-core/src/utils/isomorphic/locatorParser.ts` — utility module with locator parsing functions
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — CLI skill documentation

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
