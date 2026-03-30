#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

TARGET="extensions/bluebubbles/src/monitor-debounce.ts"

# Add normalize and sanitize functions after the type definition block
sed -i '/^type BlueBubblesDebounceEntry = {$/,/^};$/{
  /^};$/a\
\
function normalizeDebounceMessageText(text: unknown): string {\
  return typeof text === "string" ? text : "";\
}\
\
function sanitizeDebounceEntry(entry: BlueBubblesDebounceEntry): BlueBubblesDebounceEntry {\
  if (typeof entry.message.text === "string") {\
    return entry;\
  }\
  return {\
    ...entry,\
    message: {\
      ...entry.message,\
      text: "",\
    },\
  };\
}
}' "$TARGET"

# Fix combineDebounceEntries to use normalizeDebounceMessageText
sed -i 's/const text = entry\.message\.text\.trim();/const text = normalizeDebounceMessageText(entry.message.text).trim();/' "$TARGET"

# Wrap the base debouncer with sanitization at enqueue boundary
# Replace the direct debouncer assignment with a wrapper
sed -i 's/const debouncer = core\.channel\.debounce\.createInboundDebouncer/const baseDebouncer = core.channel.debounce.createInboundDebouncer/' "$TARGET"

# Add wrapper after the baseDebouncer creation block
sed -i '/targetDebouncers\.set(target, debouncer);/{
  i\
      const debouncer: BlueBubblesDebouncer = {\
        enqueue: async (item) => {\
          await baseDebouncer.enqueue(sanitizeDebounceEntry(item));\
        },\
        flushKey: (key) => baseDebouncer.flushKey(key),\
      };\

}' "$TARGET"
