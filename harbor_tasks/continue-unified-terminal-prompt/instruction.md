# Task: Fix Terminal Command Display

## Problem

The `UnifiedTerminal` component in the GUI package has a hardcoded Unix-style `$` prompt prefix that appears before terminal commands. This prefix is inappropriate for cross-platform use:

- Windows PowerShell uses `PS>`
- Windows CMD uses `>`
- The prefix doesn't reflect the user's actual shell
- The command is already visually distinct inside a labeled "Terminal" block

## What Needs to Change

In `gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx`, modify the component so that:

1. **Command display**: Commands should render without the hardcoded `$ ` prefix in the visual UI
2. **Copy functionality**: When users copy the command to clipboard, it should not include the `$ ` prefix

## Files to Modify

- `gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx` - Main component file

## Context

The component has a `copyContent` useMemo hook that creates the text for copying, and a JSX section that renders the command display. Look for where the command string is being prefixed with `$ ` in both places.

## Testing

The repository uses Vitest for testing. You can run the UnifiedTerminal tests with:

```bash
cd gui && npx vitest run UnifiedTerminal
```

## Notes

- This is a UI/UX fix for cross-platform compatibility
- The change should be minimal - just removing the hardcoded prefix
- Make sure both the display and copy functionality are updated consistently
