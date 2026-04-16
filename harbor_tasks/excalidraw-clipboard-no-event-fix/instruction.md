# Fix Clipboard Copy Without ClipboardEvent

## Problem

The clipboard copy functionality in Excalidraw silently fails when copying content without a native `ClipboardEvent` object. When `clipboardEvent` is unavailable, the code exits without attempting fallback mechanisms.

## Expected Behavior

The `copyTextToSystemClipboard` function in `packages/excalidraw/clipboard.ts` should fall back through these mechanisms when `clipboardEvent` is not available:

1. Try `navigator.clipboard.writeText` with the text/plain entry
2. If that succeeds, return (do not continue to other copy methods)
3. If that fails, fall back to `document.execCommand`

## Required Changes

### Variable declaration

The variable that finds the text/plain entry should use `const`, not `let`. The variable name is `plainTextEntry` and it finds the entry by matching `MIME_TYPES.text`.

### Return statement placement

There is a `return;` statement that should be inside the `if (clipboardEvent)` block (after processing), not outside it. Moving it inside allows the fallback mechanisms to execute when no clipboard event is available.

### After navigator.clipboard.writeText

After a successful `navigator.clipboard.writeText` call, the code should return rather than continuing. The old code set the entry to `undefined`; this should be removed and replaced with a `return;` statement.

## Verification

Run type checking after making changes:
```bash
yarn test:typecheck
```

Run all tests:
```bash
yarn test:code
yarn test:other
yarn vitest run packages/excalidraw/clipboard.test.ts
yarn vitest run packages/excalidraw/tests/clipboard.test.tsx
```