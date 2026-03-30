# fix(telegram): skip empty text replies instead of crashing with GrammyError 400

## Problem

The Telegram bot delivery module crashes with `GrammyError 400: message text is empty` when it attempts to send a whitespace-only or empty text reply via `bot.api.sendMessage()`. This happens when hooks blank out the reply text or the model emits whitespace-only content.

## Root Cause

`deliverReplies()` in `extensions/telegram/src/bot/delivery.replies.ts` checks `!reply?.text` (falsy) but does not check for semantic emptiness (whitespace-only strings). When a hook clears text to whitespace (e.g. `"   "`) or the model produces whitespace-only output, the check passes and the text reaches `sendTelegramText()`, which calls `bot.api.sendMessage()`, resulting in a Telegram API 400 error.

The direct outbound path (`send.ts`) and draft preview path already have empty guards. Only the bot delivery fan-in path is missing them.

## Expected Fix

Add a filter function that removes whitespace-only text chunks before they reach `sendTelegramText()`. Apply this filter to all three text delivery paths in `delivery.replies.ts`:
1. Normal text replies (`deliverTextReply`)
2. Follow-up text (`sendPendingFollowUpText`)
3. Voice fallback text (`sendTelegramVoiceFallbackText`)

The `message_sent` hook should still fire with `success: false` for suppressed empty replies.

## Files to Modify

- `extensions/telegram/src/bot/delivery.replies.ts`
