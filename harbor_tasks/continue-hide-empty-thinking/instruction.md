# Hide Thinking Indicator for Empty Content

## Problem

The UI is showing thinking indicators (ThinkingBlockPeek component) even when the thinking content is empty or contains only whitespace. This creates visual clutter and confusion for users.

## Affected Files

- `gui/src/components/StepContainer/StepContainer.tsx`
- `gui/src/pages/gui/Chat.tsx`

## Expected Behavior

When thinking content is empty or contains only whitespace characters (spaces, tabs, newlines), the ThinkingBlockPeek component should not be rendered at all.

### Requirements

1. **Whitespace Detection**: The code must detect when thinking content is empty or whitespace-only. Any check should use a trimming operation to determine if content is meaningful.

2. **Thinking Indicator in StepContainer**: In StepContainer.tsx, the reasoning text check must account for whitespace-only content. If the trimmed reasoning text is empty, the thinking indicator should not render.

3. **Thinking Indicator in Chat**: In Chat.tsx, when handling messages with `role === "thinking"`, the code must verify that the thinking content has meaningful text before rendering ThinkingBlockPeek. If the content is empty or whitespace-only after trimming, return `null` instead of rendering.

4. **Avoid Duplicate Rendering**: If the thinking content is extracted to a variable for the emptiness check, use that same variable when passing content to ThinkingBlockPeek rather than re-computing it.

## Validation

After fixing:
- ESLint checks must pass (`yarn lint`)
- Prettier formatting must be correct for modified files
- Core unit tests must pass