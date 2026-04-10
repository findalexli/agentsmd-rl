#!/bin/bash
set -e

echo "Applying fix for PR #21822: improve compaction to retain recent conversation context"

# Copy the fixed files from the solution directory to the repo
REPO="/workspace/opencode"

echo "Updating compaction.ts..."
cp /solution/compaction.ts "$REPO/packages/opencode/src/session/compaction.ts"

echo "Updating config.ts..."
cp /solution/config.ts "$REPO/packages/opencode/src/config/config.ts"

echo "Updating message-v2.ts..."
cp /solution/message-v2.ts "$REPO/packages/opencode/src/session/message-v2.ts"

echo "Updating compaction.txt prompt..."
cp /solution/compaction.txt "$REPO/packages/opencode/src/agent/prompt/compaction.txt"

echo "Fix applied successfully!"
