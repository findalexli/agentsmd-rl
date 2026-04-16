# Fix Notification Close Button Overlapping Description

## Problem

When `notification.open()` is called with only a `description` and no `title`, the close button overlaps the notification content. The description text currently extends underneath the close button area instead of reserving space for it.

## Symptoms

- Description-only notifications (no title) have the close button positioned on top of the text
- The right-side spacing for the close button is missing when no title is present

## Requirements

1. The title element must be conditionally rendered only when a title value is provided. When no title is present, the description element should be the first child in the DOM structure.

2. The description element must have a CSS rule using the `&:first-child` selector that applies `marginInlineEnd: token.marginSM` (using logical properties for RTL support). This reserves space on the right side for the close button.

3. Make sure existing tests still pass after the fix.
