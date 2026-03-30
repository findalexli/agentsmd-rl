#!/usr/bin/env bash
set -euo pipefail
cd /workspace/zeroclaw

TARGET="src/channels/mod.rs"

# Remove the hardcoded constant and its comment
sed -i '/^\/\/\/ Maximum history messages to keep per sender\.$/d' "$TARGET"
sed -i '/^const MAX_CHANNEL_HISTORY: usize = 50;$/d' "$TARGET"

# Replace MAX_CHANNEL_HISTORY usage with config value
sed -i 's/MAX_CHANNEL_HISTORY/ctx.prompt_config.agent.max_history_messages/g' "$TARGET"
