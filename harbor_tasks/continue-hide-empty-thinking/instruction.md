# Hide Thinking Indicator for Empty Content

## Problem

The application shows thinking indicators (via the `ThinkingBlockPeek` component) even when the thinking content is empty or contains only whitespace characters. This creates visual clutter in the UI.

## Symptoms

- When viewing chat messages, thinking blocks appear even when there's no meaningful thinking content to display
- Empty thinking sections (containing only spaces, tabs, or newlines) still render UI elements
- Messages with `role === "thinking"` that have empty content still show thinking indicators

## Expected Behavior

The `ThinkingBlockPeek` component should only render when there is actual thinking content to display. Content that is empty or contains only whitespace should not trigger the thinking indicator to appear.

The fix should check whether the thinking content is empty or whitespace-only, and if so, skip rendering the thinking block entirely (e.g., by returning `null` from the rendering logic).

## Technical Context

- The UI is a React/TypeScript application located in the `gui/` directory
- The `ThinkingBlockPeek` component is used to display thinking content to users
- Message objects have a `role` field that can be set to `"thinking"`
- Thinking content may be accessed through a `reasoning?.text` field on message items
- In `Chat.tsx`, the `renderChatMessage(message)` function generates the content string for a message

## Files to Modify

1. `gui/src/components/StepContainer/StepContainer.tsx` — Where `ThinkingBlockPeek` is rendered for step items with reasoning
2. `gui/src/pages/gui/Chat.tsx` — Where thinking messages are handled for the chat view

## Validation

After fixing:
- ESLint checks must pass (`yarn lint` in the `gui/` directory)
- Prettier formatting must be correct for modified files
- Core unit tests must pass
