# fix(channels): respect max_history_messages config in channel mode

## Problem

Channel modes (Telegram, Discord, Slack, QQ, etc.) ignore the user-configured `agent.max_history_messages` value from the configuration file. Instead, they use a hardcoded constant `MAX_CHANNEL_HISTORY = 50` to limit conversation history per sender.

CLI mode correctly uses the configured value via `trim_history()`, but channel mode bypasses this setting entirely.

## Root Cause

`src/channels/mod.rs` defines `const MAX_CHANNEL_HISTORY: usize = 50;` and uses it in `append_sender_turn()` for history trimming. This constant is never read from or connected to the configuration schema's `agent.max_history_messages` setting.

## Expected Fix

Remove the hardcoded `MAX_CHANNEL_HISTORY` constant and replace its usage in `append_sender_turn()` with `ctx.prompt_config.agent.max_history_messages` (or the equivalent config path). The default value of 50 is already preserved in the config schema, so backward compatibility is maintained.

## Files to Modify

- `src/channels/mod.rs`
