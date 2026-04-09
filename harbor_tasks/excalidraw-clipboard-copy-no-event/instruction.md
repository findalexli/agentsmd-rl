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

### Current (Broken) Behavior

The function incorrectly returns early even when `clipboardEvent` is null/undefined, preventing the fallback to `navigator.clipboard.writeText()`.

### Files to Modify

- `packages/excalidraw/clipboard.ts` - Main fix for the clipboard logic
- `packages/excalidraw/components/FilledButton.scss` - Add missing background color for success states (related styling fix included in the PR)

### Key Function

Look at `copyTextToSystemClipboard` around line 616. The issue is with the placement of return statements relative to the `if (clipboardEvent)` block.

### Related

This is a fix for a regression from PR #10710.
