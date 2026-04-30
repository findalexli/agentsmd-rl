# Add Notifications SKILL

Source: [QuantConnect/Documentation#2330](https://github.com/QuantConnect/Documentation/pull/2330)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md`

## What to add / change

## Summary

Adds a SKILL.md for the live-trading Notifications section ([03 Writing Algorithms/40 Live Trading/40 Notifications](03%20Writing%20Algorithms/40%20Live%20Trading/40%20Notifications/SKILL.md)). Same shape as the existing Writing Algorithms skills (charting, logging, scheduled-events): description, intro, critical rules, per-channel gotchas, common mistakes, and a quick checklist.

Key things the skill teaches a reviewer/author to flag:

- Notifications run in **QuantConnect Cloud live trading only** — backtests, local LEAN, and LEAN CLI live are no-ops, so call sites must be guarded with `live_mode`.
- When a channel is called from more than one site, route through a `_notify_*` helper with the recipient/credentials lifted to a module-level constant — no `live_mode` gate can be missed and the recipient is a one-line edit.
- Per-channel limits and gotchas: 10 KB email body / `attachment.txt` filename default, 1,600-char SMS / E.164 phone format, Telegram negative group-ID + bot-token + UTF-32 emoji escapes, 300 s webhook timeout + Discord `content`-key JSON envelope, FTP vs SFTP auth (password XOR private key).
- Tiered hourly free quota with paid overage; SMS always billed per message regardless of tier.
- Don't fire `notify.*` from `on_data` on minute/tick — use `on_order_event` / `on_brokerage_message` / scheduled events / state-change transitions.
- Raw subscribed-dataset content can't be sent (terms-of-use, not just quota).
- *Receiving* messages is the live-c

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
