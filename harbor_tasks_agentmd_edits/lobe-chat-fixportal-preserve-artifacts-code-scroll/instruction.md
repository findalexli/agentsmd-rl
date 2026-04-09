# Fix Portal Artifacts Code Scroll While Streaming

## Problem

When viewing code artifacts in the Portal during streaming (when the AI is generating code), the code view scrolls back to the top each time new content is received. This creates a poor user experience as users cannot follow the code being generated - it keeps jumping back to the beginning.

The issue is in the Artifacts body component where the scrollable container and the syntax highlighter interact incorrectly during content updates.

## Expected Behavior

The code view should preserve its scroll position while content is being streamed, allowing users to scroll through the code as it's being generated without it jumping back to the top.

## Files to Look At

- `src/features/Portal/Artifacts/Body/index.tsx` — Main component that renders code artifacts with syntax highlighting

## Changes Required

1. Move the `showCode` variable calculation and `isStreamingCode` flag before the early return check
2. Wrap the `Highlighter` component in a `Flexbox` container with proper overflow handling:
   - Outer container: `flex={1}`, `minHeight: 0`, `overflow: 'auto'` (handles scrolling)
   - Highlighter: `minHeight: '100%'`, `overflow: 'visible'`, `animated={isStreamingCode}` (handles content)

This separates the scroll container from the content, preventing scroll jumps when React re-renders the component during streaming.

## Config Updates

- Update `AGENTS.md` to fix branch naming convention (remove `username/` prefix from examples)
