# Fix Clipboard Copy Without ClipboardEvent

## Problem

The `copyTextToSystemClipboard` function in `packages/excalidraw/clipboard.ts` fails to properly copy text to the clipboard when called **without** a `ClipboardEvent` parameter.

### Symptom

When attempting to copy text programmatically (without an explicit clipboard event), the function exits early and never attempts to use `navigator.clipboard.writeText()` as a fallback. This was a regression introduced in a previous PR.

### Expected Behavior

The function should implement a three-tier fallback strategy:

1. **First**: Try using the provided `clipboardEvent.clipboardData.setData()` (most versatile, supports custom MIME types)
2. **Second**: If no clipboardEvent or it fails, try `navigator.clipboard.writeText()` for plain text
3. **Third**: If that fails, fall back to `document.execCommand('copy')`

When any tier succeeds, the function should not continue trying subsequent tiers.

### Additional Code Quality Issues in clipboard.ts

Within the `copyTextToSystemClipboard` function:

- The `plainTextEntry` variable should be declared with `const` rather than `let`, since it does not need reassignment.
- After successfully calling `navigator.clipboard.writeText()`, the code should not set `plainTextEntry = undefined`.

## SCSS Styling Fix

The file `packages/excalidraw/components/FilledButton.scss` is missing a background color for the success/loading button states. The selector:

```scss
&.ExcButton--status-loading,
&.ExcButton--status-success {
```

should include `background-color: var(--color-success);`.

## Files to Modify

- `packages/excalidraw/clipboard.ts`
- `packages/excalidraw/components/FilledButton.scss`
