# Fix Notification Close Button Overlapping Description

## Problem

When `notification.open()` is called with only a `description` and no `title`, the close button overlaps the notification content. The description text currently extends underneath the close button area instead of reserving space for it.

## Symptoms

- Description-only notifications (no title) have the close button positioned on top of the text
- The right-side spacing for the close button is missing when no title is present

## Requirements

1. **Conditional title rendering**: When no title is provided, the title element should not be rendered at all in the DOM. Currently the title `<div>` is always rendered even when empty. Removing it allows the description element to become the first child of the notification content area, which is needed for the CSS fix below.

2. **CSS spacing for description-only notifications**: When the description element is the first child (i.e., when there is no title), it must have `margin-inline-end` spacing to reserve space for the close button. Use a CSS selector that targets the description when it is the first child of its container (e.g., `:first-child`). Use CSS logical properties for RTL support.

3. **Verify behavior**: After the fix:
   - Rendering a notification with no title should produce NO title element in the DOM
   - The description element should be the first child of the content area (the element with `role="alert"`)
   - The generated CSS should include an `margin-inline-end` rule for the description when it is a first child
   - Rendering a notification WITH a title should still show the title element normally

4. Make sure existing tests still pass after the fix.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
