# feat(html): show repeatEachIndex when non-zero

## Problem

When running Playwright tests with the `--repeat-each` flag to repeat tests multiple times, the HTML report does not visually indicate which repetition each test result corresponds to. This makes it difficult to differentiate between repeated test runs in the report viewer.

For example, if you run `npx playwright test --repeat-each 3`, the same test appears 3 times in the report, but there's no way to tell which one is the first, second, or third repetition.

## Expected Behavior

The HTML reporter should display a `repeatEachIndex` annotation on test cases when the index is non-zero (i.e., repetitions 1, 2, 3, etc.). The first repetition (index 0) should not show this annotation to avoid clutter.

## Implementation Requirements

### Type Definition

In `packages/html-reporter/src/types.d.ts`, the `TestCaseSummary` type must include a `repeatEachIndex` field with the following signature:

```
repeatEachIndex?: number
```

### HTML Reporter

In `packages/playwright/src/reporters/html.ts`, the HTML builder must pass `repeatEachIndex` from the test object to the test case summary data. The expression used must handle the zero case by excluding it:

```
repeatEachIndex: test.repeatEachIndex || undefined
```

This ensures the field is absent (undefined) when the index is 0, so the UI knows not to display the annotation.

### Test Case View Component

In `packages/html-reporter/src/testCaseView.tsx`, implement a helper function named `appendRepeatEachIndexAnnotation` that:

1. Takes an annotations array and a `repeatEachIndex` value as parameters
2. Checks if `repeatEachIndex` is truthy using `if (repeatEachIndex)`
3. If truthy, pushes an annotation with `type: 'repeatEachIndex'` and `description: String(repeatEachIndex)` converted to a string
4. Calls this function at least twice — once for `visibleTestAnnotations` and once for `visibleAnnotations` in the result rendering path

### Files to Modify

- `packages/playwright/src/reporters/html.ts` — Add `repeatEachIndex` to test case data passed to the HTML reporter
- `packages/html-reporter/src/types.d.ts` — Add `repeatEachIndex?: number` field to `TestCaseSummary` type
- `packages/html-reporter/src/testCaseView.tsx` — Add the `appendRepeatEachIndexAnnotation` function and call it for both test and result annotations

### UI Pattern

Look at how other annotations are displayed in the test case view for guidance on the UI pattern to follow. The annotation should appear as a chip/badge in the test case details when the repetition index is non-zero.