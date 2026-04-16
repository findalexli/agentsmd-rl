# CLI: Allow Both Selectors and Locators

## Problem Description

The Playwright CLI tool currently only accepts raw CSS selectors or the internal Playwright selector format (like `role=button[name=Submit]`). Users want to use the more convenient Playwright locator syntax (like `getByRole('button', { name: 'Submit' })`) directly in CLI commands, but this results in selector parsing errors.

## Current Behavior

When using CLI commands with locator-style syntax:

```bash
# This works (raw CSS)
playwright-cli click "#submit-button"

# This works (internal selector format)
playwright-cli click "role=button[name=Submit]"

# This fails (Playwright locator syntax)
playwright-cli click "getByRole('button', { name: 'Submit' })"
```

## Expected Behavior

The CLI should accept both:
1. Traditional CSS selectors
2. Playwright locator syntax (`getByRole()`, `getByTestId()`, etc.)

## Files to Modify

1. **`packages/playwright-core/src/tools/backend/tab.ts`**
   - The `resolveSelector` method needs to use `locatorOrSelectorAsSelector()` from `locatorParser.ts` to convert Playwright locator syntax to internal selector format before using it.
   - Currently it directly passes the input to `this.page.locator()`, which doesn't understand Playwright locator syntax.

2. **`packages/playwright-core/src/tools/cli-client/skill/SKILL.md`**
   - Update the documentation to reflect the new capability
   - Change examples from `role=button[name=Submit]` to `getByRole('button', { name: 'Submit' })`
   - Add example showing `getByTestId()` usage

## Implementation Notes

The `locatorParser.ts` utility already provides `locatorOrSelectorAsSelector(language, locator, testIdAttribute)` which can convert Playwright locator strings to internal selector format. The fix involves:

1. Importing `locatorOrSelectorAsSelector` in `tab.ts`
2. Calling it with `'javascript'` as the language and the appropriate `testIdAttribute` (defaulting to `'data-testid'`)
3. Using `page.$(selector)` to check element existence (returns null if not found, unlike `locator.isVisible()` which throws)
4. Updating the documentation to match

## Testing Your Changes

After implementing the fix:
- CSS selectors like `"#main > button"` should still work
- Playwright locators like `"getByRole('button', { name: 'Submit' })"` should work
- Playwright locators like `"getByTestId('submit-button')"` should work
- The SKILL.md documentation should show the new locator syntax examples
