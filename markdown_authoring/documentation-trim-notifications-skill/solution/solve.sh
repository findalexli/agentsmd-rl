#!/usr/bin/env bash
set -euo pipefail

cd /workspace/documentation

# Idempotency guard
if grep -qF "description: Use when adding or reviewing live-trading `Notify.*` calls (Email, " "03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md b/03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: notifications
-description: Use when adding or reviewing live-trading `Notify.*` calls (Email, SMS, Telegram, Web/Webhook, FTP/SFTP) in a QuantConnect/LEAN algorithm. Notifications run in QuantConnect Cloud live trading only — backtests, local LEAN, and LEAN CLI live deployments don't have them, so guard call sites with `live_mode`. Covers per-channel limits (10 KB email body, 1,600-char SMS, 300 s webhook timeout, default `attachment.txt` filename), the tiered hourly free quota with paid overage (and SMS always billed per message regardless of tier), the rule that raw subscribed-dataset content can't be sent (terms-of-use, not just quota), the Discord webhook content-key JSON envelope, the Telegram group-ID + bot-token + UTF-32 emoji rules, that *receiving* messages is the live-commands skill not Notify, and that the right place to fire notifications is order/event/scheduled handlers, not per-bar `on_data`.
+description: Use when adding or reviewing live-trading `Notify.*` calls (Email, SMS, Telegram, Web/Webhook, FTP/SFTP) in a QuantConnect/LEAN algorithm. Notifications run in QuantConnect Cloud live trading only — backtests, local LEAN, and LEAN CLI live deployments don't have them, so guard call sites with `live_mode`. Covers per-channel limits (10 KB email body, 1,600-char SMS, 300 s webhook timeout, default `attachment.txt` filename), the tiered hourly free quota with paid overage (SMS always billed per message regardless of tier), the rule that raw subscribed-dataset content can't be sent (terms-of-use), the Discord webhook content-key JSON envelope, the Telegram group-ID + bot-token + UTF-32 emoji rules, that *receiving* messages is the live-commands skill, and that `notify.*` belongs in event handlers, not per-bar `on_data`.
 ---
 
 # Notifications in QuantConnect / LEAN
@@ -9,12 +9,7 @@ Notifications send messages **out** of a live-trading algorithm — to email, SM
 
 ## Critical: Cloud live trading only
 
-Notifications are wired up exclusively in QuantConnect Cloud live trading.
-
-- **Backtests** — the call doesn't reach an external recipient.
-- **Local LEAN** and **LEAN CLI live deployments** — the notification services aren't available.
-
-Guard every notification call with `self.live_mode` so the call sites are obvious and no companion logging fires in backtests:
+Notifications are wired up exclusively in QuantConnect Cloud live trading. They are no-ops in **backtests**, **local LEAN**, and **LEAN CLI live deployments**. Guard every call with `self.live_mode` so the call sites are obvious and no companion logging fires in backtests:
 
 ```python
 if self.live_mode:
@@ -23,7 +18,7 @@ if self.live_mode:
 
 ## Wrap repeated calls in a helper
 
-When the same channel is used in more than one place, route every call through a private helper so the address/phone/group-ID/token/filename and the `live_mode` gate live in **one** place. Lift the recipient/credentials to **module-level constants** at the top of the file — the user reads them as config, edits them in one place, and no `initialize` plumbing is needed.
+When the same channel is used in more than one place, route every call through a private helper so the address/phone/group-ID/token/filename and the `live_mode` gate live in **one** place. Lift the recipient/credentials to **module-level constants** at the top of the file — the user reads them as config and edits them in one place.
 
 ```python
 OPS_EMAIL = "ops@example.com"
@@ -35,7 +30,7 @@ class MyAlgorithm(QCAlgorithm):
             self.notify.email(OPS_EMAIL, subject, message)
 ```
 
-Apply the same pattern to the other channels — `_notify_sms`, `_notify_telegram` (so `id` and `token` aren't repeated), `_notify_web` (so the URL and any auth header aren't repeated), `_notify_ftp` (so hostname/username/password aren't repeated). One-off notifications can stay inline; the helper pays for itself once a channel is called from two or more sites.
+Apply the same pattern to other channels — `_notify_sms`, `_notify_telegram`, `_notify_web`, `_notify_ftp`. One-off notifications can stay inline.
 
 ## The five channels
 
@@ -48,13 +43,13 @@ notify.ftp(hostname, username, password, file_path, file_content, port=None)
 notify.sftp(hostname, username, password|private_key + private_key_passphrase, file_path, file_content, port=None)
 ```
 
-| Channel | Body limit | Cost model |
-| --- | --- | --- |
-| Email | 10 KB body, optional named attachment | Free under hourly quota; 1 QCC each over |
-| SMS | 1,600 chars; phone must be E.164 (`+1...`) | **Always paid: 1 QCC US/CA, 10 QCC international per message** |
-| Telegram | Plain text via bot in a group | Free under hourly quota; 1 QCC each over |
-| Web (HTTP POST) | 300 s response timeout on the receiver | Free under hourly quota; 1 QCC each over |
-| FTP / SFTP | Sends file content under `file_path` | Free under hourly quota; 1 QCC each over |
+| Channel | Body limit |
+| --- | --- |
+| Email | 10 KB body, optional named attachment |
+| SMS | 1,600 chars; phone must be E.164 (`+1...`) |
+| Telegram | Plain text via bot in a group |
+| Web (HTTP POST) | 300 s response timeout on the receiver |
+| FTP / SFTP | Sends file content under `file_path` |
 
 ### Hourly free quota by tier
 
@@ -66,11 +61,11 @@ notify.sftp(hostname, username, password|private_key + private_key_passphrase, f
 | Trading Firm | 240 |
 | Institution | 3,600 |
 
-The hourly quota covers email, FTP, Telegram, and webhook combined; **SMS is excluded** and billed per message regardless of tier. Overage on the other channels costs 1 QCC per notification.
+The hourly quota covers email, FTP, Telegram, and webhook combined; overage costs 1 QCC per notification. **SMS is excluded** and always billed per message regardless of tier (1 QCC US/CA, 10 QCC international).
 
 ## Critical: Don't fire per-bar — fire on events
 
-Putting `notify.*` inside `on_data` on minute or tick resolution will saturate the hourly quota in seconds and burn QCC for the rest of the hour. Notifications belong on events, not on bars:
+Putting `notify.*` inside `on_data` on minute or tick resolution saturates the hourly quota in seconds and burns QCC. Notifications belong on events:
 
 - `on_order_event` (filled / canceled / rejected)
 - `on_brokerage_message` (broker errors, disconnects)
@@ -82,51 +77,31 @@ Putting `notify.*` inside `on_data` on minute or tick resolution will saturate t
 
 **Email.** Without `headers={'filename': '...'}` the attachment is named `attachment.txt`. Body cap is 10 KB — large diagnostic dumps belong in the attachment or in the Object Store, not inlined in `message`.
 
-**SMS.** `phone_number` must be E.164: `+` followed by country code and digits, no spaces or dashes (`+14155551234`, not `(415) 555-1234`). SMS is the only channel that doesn't need internet on the receiver, but also the only channel without a free quota — every message costs QCC. Reserve SMS for genuinely urgent alerts (broker disconnects, halt-trading); use email/Telegram/webhook for routine notifications.
+**SMS.** `phone_number` must be E.164 (`+14155551234`, not `(415) 555-1234`). It's the only channel without a free quota, so reserve it for genuinely urgent alerts (broker disconnects, halt-trading) and use email/Telegram/webhook for routine notifications.
 
-**Telegram.** `id` is the **group ID** as it appears in the Telegram web URL — a negative integer like `-503016366`. The `token` argument is optional **only** if `@quantconnect_notifications_bot` has been added to the group; otherwise the user must create their own bot via `@BotFather` and pass that bot's token. Emojis must be encoded as UTF-32 escape sequences (`'\U0001f680'` for rocket); pasting the literal emoji often fails the Telegram API encoding.
+**Telegram.** `id` is the **group ID** as it appears in the Telegram web URL — a negative integer like `-503016366`. The `token` argument is optional **only** if `@quantconnect_notifications_bot` has been added to the group; otherwise create a bot via `@BotFather` and pass its token. Emojis must be UTF-32 escape sequences (`'\U0001f680'`); literal emoji characters fail the Telegram API encoding.
 
-**Webhook.** HTTP POST with a 300 s response timeout — endpoints that block on synchronous expensive work will silently time out, and the algorithm has no built-in retry. Discord webhooks expect a JSON body with a `content` key, not a plain string — wrap with `json.dumps({'content': ...})`. Sending a plain string to a Discord URL is rejected by Discord with no visible error in the algorithm.
+**Webhook.** HTTP POST with a 300 s response timeout — endpoints that block on synchronous expensive work silently time out, and there is no built-in retry. Discord webhooks expect a JSON body keyed on `content`, not a plain string — wrap with `json.dumps({'content': ...})`. A plain string to a Discord URL is rejected with no visible error in the algorithm.
 
-**FTP vs SFTP.** `notify.ftp` is plaintext. `notify.sftp` is SSH FTP and accepts either `password=` **or** `private_key=` (with optional `private_key_passphrase=`), not both. Pick the auth mode that matches the server.
+**FTP vs SFTP.** `notify.ftp` is plaintext. `notify.sftp` is SSH FTP and accepts either `password=` **or** `private_key=` (with optional `private_key_passphrase=`), not both.
 
 ## Don't send subscribed dataset content
 
 The notification system **can't be used for data distribution** — that's a terms-of-use violation, not just a quota concern. Send derived information (signal value, portfolio value, fill summary), not raw bars/quotes/trades from QuantConnect-subscribed datasets. The logging skill carries the same rule.
 
 ## Receiving messages
 
-Notify is one-way out. If the algorithm needs to *receive* external instructions (manual liquidate, parameter change), that's the live-commands skill, not Notify.
-
-## Common mistakes to avoid
-
-- **Calling `notify.*` in a backtest expecting it to test the integration** — it doesn't reach an external recipient. Test in a deployed cloud paper-trade live algorithm.
-- **Calling `notify.*` from local LEAN or LEAN CLI live** — services aren't available; cloud live only.
-- **No `live_mode` guard** — leaves the call site ambiguous and fires accompanying logs in backtests.
-- **Firing in `on_data` on minute/tick resolution** — exhausts the hourly free quota in seconds and starts billing QCC. Move to event handlers or guard with a state-change condition that only fires on the transition.
-- **Using SMS for non-urgent alerts** — every SMS costs QCC. Use email/Telegram/webhook for routine notifications, SMS only for urgent ones.
-- **Phone numbers in local format (`(415) 555-1234`)** — must be E.164 (`+14155551234`).
-- **Email attachment without `headers={'filename': '...'}`** — defaults to `attachment.txt`.
-- **Email body over 10 KB** — capped; large dumps belong in the attachment.
-- **Telegram emoji as a literal Unicode character** — encode as UTF-32 escape (`\U0001f680`).
-- **Telegram with no `token` and no `@quantconnect_notifications_bot` in the group** — silently fails.
-- **Telegram `id` as a positive number** — group IDs are negative integers (`-503016366`).
-- **Discord webhook with a plain string body** — Discord requires a JSON body with a `content` key.
-- **Webhook receiver that blocks longer than 300 s** — request times out, no retry.
-- **Mixing `password=` and `private_key=` in `notify.sftp`** — pick one auth mode.
-- **Sending raw bars/quotes/trades from a subscribed dataset** — terms-of-use violation. Send derived/aggregated values instead.
-- **Trying to *receive* messages with `notify.*`** — it's send-only.
+Notify is one-way out. To *receive* external instructions (manual liquidate, parameter change), use the live-commands skill.
 
 ## Quick checklist when adding a notification
 
 1. Is the call gated with `self.live_mode`?
-2. If the channel is used more than once, is the call routed through a `_notify_*` helper so the recipient/credentials and `live_mode` gate live in one place?
+2. If the channel is used more than once, is the call routed through a `_notify_*` helper with the recipient/credentials lifted to module-level constants?
 3. Is the call site an event handler or per-bar `on_data`? If per-bar, can it be gated to a real state change?
-4. For SMS: is the alert urgent enough to justify per-message QCC cost? Phone number in E.164 format?
+4. For SMS: is the alert urgent enough to justify per-message QCC cost? Phone number in E.164 format and body under 1,600 chars?
 5. For email: is the attachment filename set via `headers={'filename': ...}` and the body under 10 KB?
 6. For Telegram: group ID a negative integer, bot present in group (or `token` passed), emojis as UTF-32 escapes?
 7. For webhook: receiver responds within 300 s? Discord targets wrapped in a `content`-keyed JSON object?
 8. For FTP vs SFTP: auth method matches the server (password vs SSH key, not both)?
 9. Does the message body contain raw subscribed-dataset content? If yes, swap for a derived value.
-10. Is SMS body under 1,600 chars?
-11. Does the algorithm need to *receive* messages? That's the live-commands skill.
+10. Does the algorithm need to *receive* messages? That's the live-commands skill.
PATCH

echo "Gold patch applied."
