# feat(html): show repeatEachIndex when non-zero

## Problem

When running Playwright tests with the `--repeat-each` flag to repeat tests multiple times, the HTML report does not visually indicate which repetition each test result corresponds to. This makes it difficult to differentiate between repeated test runs in the report viewer.

For example, if you run `npx playwright test --repeat-each 3`, the same test appears 3 times in the report, but there's no way to tell which one is the first, second, or third repetition.

## Expected Behavior

The HTML reporter should display a `repeatEachIndex` annotation on test cases when the index is non-zero (i.e., repetitions 1, 2, 3, etc.). The first repetition (index 0) should not show this annotation to avoid clutter.

Specifically:

1. The `TestCaseSummary` type definition must include an optional `repeatEachIndex` field of type `number`
2. The HTML reporter must pass the `repeatEachIndex` value from the test object to the test case data
3. The test case view component must add this as an annotation that displays in the UI:
   - The annotation type must be the string `'repeatEachIndex'`
   - The annotation description should be the index value converted to a string
   - The annotation should only be added when the index is non-zero (zero should be excluded)
   - The annotation should appear for both test-level and result-level annotations in the component

## Files to Modify

- `packages/playwright/src/reporters/html.ts` — Pass `repeatEachIndex` to test case data
- `packages/html-reporter/src/types.d.ts` — Add `repeatEachIndex` field to `TestCaseSummary` type
- `packages/html-reporter/src/testCaseView.tsx` — Add logic to display the annotation for both test and result annotations

## Implementation Pattern

Look at how other annotations are displayed in the test case view for guidance on the UI pattern to follow. The annotation should only be created when the repeatEachIndex value is truthy (non-zero), and should appear as a chip/badge in the test case details.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
