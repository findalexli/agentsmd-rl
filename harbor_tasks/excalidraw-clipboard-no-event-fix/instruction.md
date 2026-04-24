# Fix Clipboard Copy Without ClipboardEvent

## Problem

The clipboard copy functionality in Excalidraw silently fails when copying content without a native `ClipboardEvent` object. When `clipboardEvent` is unavailable, the code exits before attempting any fallback mechanisms.

## Symptom

When `copyTextToSystemClipboard` is called without a `ClipboardEvent` argument:
1. The function returns early without trying `navigator.clipboard.writeText`
2. No error is thrown, but the clipboard content is not written
3. The fallback copy method (`copyTextViaExecCommand`) is never reached

This can be verified by calling `copyTextToSystemClipboard({[MIME_TYPES.text]: "hello"}, null)` — the text is not copied to clipboard.

## Expected Behavior

The `copyTextToSystemClipboard` function should:
1. If `clipboardEvent` is provided and works, return early (success)
2. If no `clipboardEvent` or it fails, fall back to `navigator.clipboard.writeText`
3. If `navigator.clipboard.writeText` succeeds, return (success)
4. If it fails, fall back to `document.execCommand`

## File

`packages/excalidraw/clipboard.ts` — function `copyTextToSystemClipboard`

## Verification

After fixing, run:
```bash
yarn test:typecheck
yarn test:code
yarn test:other
yarn vitest run packages/excalidraw/clipboard.test.ts
yarn vitest run packages/excalidraw/tests/clipboard.test.tsx
```