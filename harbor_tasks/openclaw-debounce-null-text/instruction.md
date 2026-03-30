# fix(bluebubbles): guard debounce flush against null text

## Problem

The BlueBubbles debounce flush crashes with `TypeError: Cannot read properties of null (reading 'trim')` when processing a message entry whose `text` field is null. This happens when a webhook delivers a tapback/reaction-only message with no text content.

## Root Cause

`combineDebounceEntries()` in `extensions/bluebubbles/src/monitor-debounce.ts` calls `entry.message.text.trim()` without a null guard. When a webhook delivers a message with null text (e.g. tapback/reaction-only), the multi-entry flush path crashes because `.trim()` is called on null.

## Expected Fix

1. Add a normalization function that coerces null/undefined message text to an empty string.
2. Apply this normalization at two points:
   - At the debounce enqueue boundary (sanitize entries before they enter the queue)
   - Inside `combineDebounceEntries()` as a defensive guard for entries already queued
3. The fix should ensure that null-text entries are silently skipped during combination, while valid text entries in the same flush batch are still processed and delivered.

## Files to Modify

- `extensions/bluebubbles/src/monitor-debounce.ts`
