# Task: Fix Empty Thinking Content Display

## Problem

The Continue IDE extension shows a "thinking" indicator for AI model responses that include reasoning/thinking blocks. However, this indicator is incorrectly displayed even when the thinking content is empty or contains only whitespace characters. This creates visual clutter and confusing UI elements.

## Files to Modify

1. **gui/src/components/StepContainer/StepContainer.tsx** - Handles inline reasoning text rendering
2. **gui/src/pages/gui/Chat.tsx** - Handles thinking role message rendering

## What Needs to Happen

### In StepContainer.tsx:
The component currently checks `props.item.reasoning?.text` before rendering a `ThinkingBlockPeek` component. This check passes for whitespace-only strings. Change this to use `.trim()` so that empty or whitespace-only content doesn't trigger the thinking indicator.

### In Chat.tsx:
The component renders thinking role messages by calling `renderChatMessage(message)` directly in the `ThinkingBlockPeek` component. Before rendering, you need to:
1. Extract the thinking content into a variable
2. Check if that content is empty or whitespace-only using `.trim()`
3. Return `null` (don't render anything) if the content is empty
4. Only render the `ThinkingBlockPeek` with the extracted content if it's non-empty

## Testing Your Fix

The fix should ensure:
- Empty thinking blocks ("" or "   " or "\n") do not show the thinking indicator
- Actual thinking content still displays the thinking indicator normally
- TypeScript compiles without errors

## Hints

- The `.trim()` method on strings removes leading/trailing whitespace and returns an empty string for whitespace-only content
- An empty string is falsy in JavaScript/TypeScript, so `!"   ".trim()` evaluates to `true`
- The change in Chat.tsx requires extracting the content first, then conditionally returning null or the component
