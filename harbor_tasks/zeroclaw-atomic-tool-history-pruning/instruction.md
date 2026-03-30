# fix(agent): treat tool_use/tool_result as atomic groups in history pruning

## Problem

The history pruner can orphan tool messages by dropping an assistant message (containing tool_use blocks) without also dropping its consecutive tool result messages (or vice versa). This breaks tool_use/tool_result pairing required by providers like Anthropic, causing API 400 errors.

## Root Cause

Both `emergency_history_trim()` in `src/agent/history.rs` and `prune_history()` in `src/agent/history_pruner.rs` treat each message independently when collapsing or dropping. An assistant message with tool calls and its subsequent tool result messages form a logical group, but the pruner can remove individual messages from this group.

## Expected Fix

1. In `src/agent/history.rs` (`emergency_history_trim`):
   - When encountering an assistant message, count consecutive following tool messages
   - Drop the assistant + all its tool messages as an atomic group

2. In `src/agent/history_pruner.rs` (`prune_history`):
   - Phase 1 (collapse): When collapsing tool results, handle an assistant message followed by multiple consecutive tool messages as a single group. Collapse the entire group into one summary assistant message.
   - Phase 2 (budget enforcement): When dropping messages to fit the token budget, drop assistant+tool groups atomically. Never leave orphaned tool messages.

The invariant to maintain: after pruning, every tool message must be immediately preceded by an assistant message.

## Files to Modify

- `src/agent/history.rs`
- `src/agent/history_pruner.rs`
