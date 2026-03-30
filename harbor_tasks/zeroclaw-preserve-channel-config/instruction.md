# fix(onboard): preserve existing channel config when re-configuring

## Problem

Running the channels repair wizard (`run_channels_repair_wizard`) overwrites all existing channel configuration values. When a user re-configures channels (e.g. to add a new channel), their existing channel settings (tokens, allowed users, etc.) are lost and replaced with defaults.

## Root Cause

The `setup_channels()` function in `src/onboard/wizard.rs` always starts from `ChannelsConfig::default()`. When called from `run_channels_repair_wizard()`, the existing configuration is discarded. Each channel setup prompt also starts fresh without pre-populating existing values.

## Expected Fix

1. Change `setup_channels()` to accept an `Option<ChannelsConfig>` parameter for existing config
2. When called from `run_wizard()` (fresh setup), pass `None`
3. When called from `run_channels_repair_wizard()`, pass `Some(config.channels_config.clone())`
4. Inside `setup_channels()`, use `existing.unwrap_or_default()` instead of `ChannelsConfig::default()`
5. For each channel's setup prompts, pre-populate with existing values (e.g. show "Enter to keep existing" for tokens, default allowed users from existing config)

## Files to Modify

- `src/onboard/wizard.rs`
