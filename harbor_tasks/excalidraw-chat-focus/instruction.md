# Task: Fix Input Focus During AI Generation in Chat Interface

## Problem Description

In the Excalidraw chat interface (`TTDDialog/Chat`), there's a focus management issue during AI generation:

**Symptom:** When the AI is generating a diagram and the user presses Enter, the input textarea loses focus. This happens because:

1. The input is disabled during generation (via `disabled={isGenerating || ...}`)
2. The Enter key handler calls `handleSubmit()` unconditionally

Both of these behaviors together cause a poor user experience - users can't see that generation is in progress (no visual feedback), and the input loses focus making it hard to continue the conversation.

## Files to Modify

**Primary file:**
- `packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx`

**Secondary file (for localization):**
- `packages/excalidraw/locales/en.json`

## Expected Behavior

After the fix:

1. **Input remains enabled** during generation (don't disable it based on `isGenerating`)
2. **Enter key is blocked** from submitting when `isGenerating` is true (guard the `handleSubmit()` call)
3. **Placeholder changes** to show "Generating..." when `isGenerating` is true
4. **Visual indicator** shows the generating state (e.g., border color change on the input wrapper)
5. **Localization string** for "Generating..." is added to `en.json`

## Hints

- Look at the `handleKeyDown` function in `ChatInterface.tsx`
- Look at the `disabled` prop on the textarea element
- Look at the `placeholder` prop - it's a nested ternary that needs a new first condition
- The input wrapper div (`chat-interface__input-wrapper`) can have a `style` prop for visual feedback

## Testing

Your changes should maintain TypeScript compatibility. The repo uses `yarn test:typecheck` for type checking.

Remember to add the localization string to `en.json` under the `"chat"` section.
