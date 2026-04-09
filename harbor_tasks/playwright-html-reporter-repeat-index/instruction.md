# feat(html): show repeatEachIndex when non-zero

## Problem

When running Playwright tests with the `--repeat-each` flag to repeat tests multiple times, the HTML report does not visually indicate which repetition each test result corresponds to. This makes it difficult to differentiate between repeated test runs in the report viewer.

For example, if you run `npx playwright test --repeat-each 3`, the same test appears 3 times in the report, but there's no way to tell which one is the first, second, or third repetition.

## Expected Behavior

The HTML reporter should display a `repeatEachIndex` annotation on test cases when the index is non-zero (i.e., repetitions 1, 2, 3, etc.). The first repetition (index 0) should not show this annotation to avoid clutter.

## Files to Look At

- `packages/playwright/src/reporters/html.ts` — The HTML reporter that generates test report data. This file creates the `TestCaseSummary` objects that are passed to the HTML reporter UI.

- `packages/html-reporter/src/types.d.ts` — TypeScript type definitions for the HTML reporter. You may need to add the `repeatEachIndex` field to the appropriate type(s).

- `packages/html-reporter/src/testCaseView.tsx` — React component that renders individual test case details in the HTML report. This is where the annotation display logic should be added.

## Implementation Hints

1. The HTML reporter (`html.ts`) has access to `test.repeatEachIndex` which indicates which repetition of the test this is (0-indexed).

2. The `repeatEachIndex` should only be included in the output when it's non-zero (to avoid cluttering the UI for the common case of no repetition).

3. In the test case view component, you'll need to add an annotation when `repeatEachIndex` is present and non-zero.

4. Look at how other annotations are displayed in the test case view for guidance on the UI pattern to follow.
