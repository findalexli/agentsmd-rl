# fix(telegram): split long messages at word boundaries instead of mid-word

## Problem

When Telegram messages need to be split because they exceed the character limit, the splitting algorithm cuts words in the middle rather than at word boundaries. This produces garbled output where words are broken across chunks.

## Root Cause

`splitTelegramChunkByHtmlLimit()` in `extensions/telegram/src/format.ts` uses a proportional estimate from rendered HTML length to find the split point. When HTML escaping expands characters (e.g. `<` becomes `&lt;`), the estimate window becomes too short to reach the next whitespace boundary, and `findMarkdownIRPreservedSplitIndex` falls back to a hard cut at `maxEnd` -- mid-word.

## Expected Fix

1. Replace the proportional text estimate with a search that finds the largest text prefix whose rendered Telegram HTML fits within the character limit.
2. Split at the last whitespace boundary within the verified prefix.
3. Single words longer than the limit should still hard-split (unavoidable).
4. Markdown formatting must stay balanced across split points (e.g. `<b>...</b>` tags).

The key change is in `splitTelegramChunkByHtmlLimit` -- it should use exact HTML length checks rather than proportional estimates.

## Files to Modify

- `extensions/telegram/src/format.ts`
