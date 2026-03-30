#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

TARGET="extensions/telegram/src/bot/delivery.replies.ts"

# Add filter function after markDelivered function
sed -i '/^function markDelivered(progress: DeliveryProgress): void {$/,/^}$/{
  /^}$/a\
\
function filterEmptyTelegramTextChunks<T extends { text: string }>(chunks: readonly T[]): T[] {\
  // Telegram rejects whitespace-only text payloads; drop them before sendMessage so\
  // hook-mutated or model-emitted empty replies become a no-op instead of a 400.\
  return chunks.filter((chunk) => chunk.text.trim().length > 0);\
}
}' "$TARGET"

# Path 1: deliverTextReply - wrap chunkText call with filter
sed -i 's/chunks: params\.chunkText(params\.replyText),/const chunks = filterEmptyTelegramTextChunks(params.chunkText(params.replyText));\n    chunks,/' "$TARGET"

# Path 2: sendPendingFollowUpText - wrap chunkText call with filter
sed -i '/sendPendingFollowUpText/,/sendChunkedTelegramReplyText/{
  s/chunks: params\.chunkText(params\.text),/const chunks = filterEmptyTelegramTextChunks(params.chunkText(params.text));\n    chunks,/
}' "$TARGET"

# Path 3: sendTelegramVoiceFallbackText - wrap chunkText call with filter
sed -i '/sendTelegramVoiceFallbackText/,/for (let i = 0/{
  s/const chunks = opts\.chunkText(opts\.text);/const chunks = filterEmptyTelegramTextChunks(opts.chunkText(opts.text));/
}' "$TARGET"
