# Fix retries and related UX issues in Text-to-Diagram chat

The Text-to-Diagram (TTD) chat feature has several UX issues that need fixing:

## Issues to Fix

### 1. Scroll flicker in chat interface
When messages are added to the chat, there's a visible flicker caused by the scroll happening after the paint. The chat uses `useEffect` for auto-scrolling, but this runs after React renders to the DOM, causing frame+1 flicker.

**Files:** `packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx`

### 2. Parse error repair buttons shown incorrectly
The repair/edit buttons for parse errors are currently shown for ALL parse error messages in the chat history. They should only be shown for the LAST message when it's a parse error (users shouldn't be able to repair old messages).

**Files:** `packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx`, `packages/excalidraw/components/TTDDialog/Chat/ChatMessage.tsx`

### 3. Inconsistent onGenerate API
The `onGenerate` function is called with positional parameters in some places and inconsistently across the codebase. Standardize it to use an object parameter with `prompt` and optional `isRepairFlow` properties.

**Files:** `packages/excalidraw/components/TTDDialog/types.ts`, `packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts`, `packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx`, `packages/excalidraw/components/TTDDialog/Chat/TTDChatPanel.tsx`, `packages/excalidraw/components/TTDDialog/TextToDiagram.tsx`

### 4. Regeneration doesn't show pending state immediately
When regenerating (repair flow), the UI doesn't immediately show the pending/loading state with empty content. It only updates the state on network errors, but should always reset the state for regeneration.

**Files:** `packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts`

### 5. Type safety issues
- `useTTDChatStorage.ts` uses truthy check for content when it should use `typeof` check
- `utils/chat.ts` uses `findLastIndex` array method which may not be available

**Files:** `packages/excalidraw/components/TTDDialog/useTTDChatStorage.ts`, `packages/excalidraw/components/TTDDialog/utils/chat.ts`

## Expected Behavior

1. Chat should scroll smoothly without flicker when new messages arrive
2. Repair buttons should only appear on the most recent message if it has a parse error
3. All onGenerate calls should use consistent object syntax: `onGenerate({ prompt: "...", isRepairFlow: true })`
4. When regenerating, the UI should immediately show loading state and clear previous content
5. Type checks should be robust against non-string content values

## Development Notes

- This is a React/TypeScript codebase using hooks
- Run `yarn test:typecheck` to verify TypeScript compilation
- The TTDDialog components handle text-to-diagram generation with a chat interface
- Look at the component props and types to understand the data flow
