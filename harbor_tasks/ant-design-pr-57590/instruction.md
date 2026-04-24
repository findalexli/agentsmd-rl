# Fix Notification Close Button Overlap

The Notification component has a layout bug when rendering notifications that have only a description without a title.

## Symptom

When a notification is opened with only a `description` prop (no `title`), the close button overlaps with the description text. This creates a poor user experience where text is unreadable behind the close button.

## Expected Behavior

The notification panel should render correctly regardless of whether a title is provided. When only description is present, the description should be readable and not overlap with the close button.

## Files

- `components/notification/PurePanel.tsx`
- `components/notification/style/index.ts`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
