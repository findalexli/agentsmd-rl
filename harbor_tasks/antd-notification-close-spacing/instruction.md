# Fix Notification Close Button Overlap

## Problem

When `notification.open()` is called with only a `description` and no `title`, the close button overlaps the notification content. This happens because the right-side spacing for the close button is only reserved when a title block exists.

## Expected Behavior

The notification should have consistent spacing whether a title is present or not. The close button should never overlap the content.

## Affected Files

1. `components/notification/PurePanel.tsx` - The main component that renders notification content
2. `components/notification/style/index.ts` - CSS-in-JS styles for the notification component
3. `components/notification/__tests__/index.test.tsx` - Test file (minor formatting)

## What You Need To Do

1. **Modify `PurePanel.tsx`**: The title block is currently always rendered. Change it to only render when `title` prop is truthy. This prevents an empty title div from taking up layout space while not reserving close-button spacing.

2. **Modify `style/index.ts`**: When there's no title, the description becomes the first child and needs right margin to reserve space for the close button. Add a CSS rule for `&:first-child` on the description block that adds `marginInlineEnd` using the design token `token.marginSM`.

3. **Update the test file**: Add proper blank line formatting before the "When closeIcon is null" describe block.

## Key Implementation Details

- The fix uses CSS logical properties (`marginInlineEnd`) for RTL support
- Spacing must use design tokens (`token.marginSM`) - never hardcode pixel values
- Use the conditional rendering pattern: `{title && (<div>...</div>)}`

## Design Tokens Reference

Ant Design uses a design token system. For this fix:
- `token.marginSM` - Small margin (typically 12px)
- `token.marginXS` - Extra small margin (used for marginTop on description)

## How to Test

Run the notification tests:
```bash
npm test -- --testPathPattern=notification --no-coverage
```

Check TypeScript compilation:
```bash
npx tsc --noEmit --skipLibCheck
```
