#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

TARGET="extensions/telegram/src/bot/delivery.replies.ts"

python3 << 'PYEOF'
import re

path = "extensions/telegram/src/bot/delivery.replies.ts"
with open(path) as f:
    content = f.read()

# 1. Add filterEmptyTelegramTextChunks after markDelivered closing brace
filter_fn = """
function filterEmptyTelegramTextChunks<T extends { text: string }>(chunks: readonly T[]): T[] {
  // Telegram rejects whitespace-only text payloads; drop them before sendMessage so
  // hook-mutated or model-emitted empty replies become a no-op instead of a 400.
  return chunks.filter((chunk) => chunk.text.trim().length > 0);
}"""

content = content.replace(
    "  progress.deliveredCount += 1;\n}",
    "  progress.deliveredCount += 1;\n}" + filter_fn,
    1,
)

# 2. Path 1 (deliverTextReply): extract chunk computation before sendChunkedTelegramReplyText
content = content.replace(
    "  let firstDeliveredMessageId: number | undefined;\n"
    "  await sendChunkedTelegramReplyText({\n"
    "    chunks: params.chunkText(params.replyText),",
    "  let firstDeliveredMessageId: number | undefined;\n"
    "  const chunks = filterEmptyTelegramTextChunks(params.chunkText(params.replyText));\n"
    "  await sendChunkedTelegramReplyText({\n"
    "    chunks,",
    1,
)

# 3. Path 2 (sendPendingFollowUpText): same pattern with params.text
content = content.replace(
    "}): Promise<void> {\n"
    "  await sendChunkedTelegramReplyText({\n"
    "    chunks: params.chunkText(params.text),",
    "}): Promise<void> {\n"
    "  const chunks = filterEmptyTelegramTextChunks(params.chunkText(params.text));\n"
    "  await sendChunkedTelegramReplyText({\n"
    "    chunks,",
    1,
)

# 4. Path 3 (sendTelegramVoiceFallbackText): wrap existing assignment
content = content.replace(
    "  const chunks = opts.chunkText(opts.text);",
    "  const chunks = filterEmptyTelegramTextChunks(opts.chunkText(opts.text));",
    1,
)

with open(path, "w") as f:
    f.write(content)
PYEOF
