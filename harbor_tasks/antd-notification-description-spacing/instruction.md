# Fix Notification Close Button Overlapping Description

## Problem

When `notification.open()` is called with only a `description` and no `title`, the close button overlaps the notification content. The description text currently extends underneath the close button area instead of reserving space for it.

## Symptoms

- Description-only notifications (no title) have the close button positioned on top of the text
- The right-side spacing for the close button is missing when no title is present

## Requirements

1. When no title is provided, the title element should not be rendered at all. This allows the description element to become the first child in the DOM structure, enabling CSS selectors to target it specifically.

2. When the description element is the first child (i.e., when there is no title), it must have appropriate CSS spacing on the inline-end side (right side in LTR, left side in RTL) to reserve space for the close button. Use CSS logical properties (for RTL support) and design tokens for spacing values.

3. Make sure existing tests still pass after the fix.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
