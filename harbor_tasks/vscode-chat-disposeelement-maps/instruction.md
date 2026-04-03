# Fix Memory Leak in Chat List Renderer Element Maps

The chat list renderer in VS Code (`src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts`) maintains several maps to track code blocks, file trees, and focused file trees by response ID and editor URI. When chat list elements are scrolled out of the viewport and disposed, these maps are never cleaned up.

This causes a memory leak where entries for disposed elements accumulate in:
- `codeBlocksByResponseId`
- `codeBlocksByEditorUri`
- `fileTreesByResponseId`
- `focusedFileTreesByResponseId`

Since these maps are only read for the focused response (which is always visible), it is safe to clean up entries when elements leave the viewport during the dispose/recycle phase.

Add cleanup logic in the element dispose path to delete entries from all four maps.
