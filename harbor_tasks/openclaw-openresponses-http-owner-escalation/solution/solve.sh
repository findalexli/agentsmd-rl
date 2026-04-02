#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

FILE="src/gateway/openresponses-http.ts"

# Idempotency check
if grep -q 'senderIsOwner: boolean;' "$FILE" 2>/dev/null &&
   grep -q 'senderIsOwner: params.senderIsOwner,' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Step 1: Add senderIsOwner: boolean to the runResponsesAgentCommand params type
# Insert after "messageChannel: string;" in the params block
sed -i '/^  messageChannel: string;$/a\  senderIsOwner: boolean;' "$FILE"

# Step 2: Replace the hardcoded senderIsOwner: true with params.senderIsOwner
# Also remove the misleading comment above it
sed -i '/\/\/ HTTP API callers are authenticated operator clients for this gateway context\./d' "$FILE"
sed -i 's/      senderIsOwner: true,/      senderIsOwner: params.senderIsOwner,/' "$FILE"

# Step 3: Add senderIsOwner: false to both call sites in handleOpenResponsesHttpRequest
# These are the two places where runResponsesAgentCommand is called with an object literal
# containing messageChannel, followed by deps — insert senderIsOwner: false between them
sed -i '/^        messageChannel,$/a\        senderIsOwner: false,' "$FILE"

echo "Patch applied successfully."
