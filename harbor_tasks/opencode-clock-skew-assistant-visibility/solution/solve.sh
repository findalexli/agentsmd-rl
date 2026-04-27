#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

TARGET="packages/ui/src/components/session-turn.tsx"

if grep -q 'for (let i = 0; i < messages.length; i++)' "$TARGET" \
   && ! grep -q 'item.role === "user") break' "$TARGET"; then
    echo "solve.sh: patch already applied; nothing to do"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/ui/src/components/session-turn.tsx b/packages/ui/src/components/session-turn.tsx
index 75279a90e666..61123b180e26 100644
--- a/packages/ui/src/components/session-turn.tsx
+++ b/packages/ui/src/components/session-turn.tsx
@@ -267,14 +267,12 @@ export function SessionTurn(
       if (!msg) return emptyAssistant

       const messages = allMessages() ?? emptyMessages
-      const index = messageIndex()
-      if (index < 0) return emptyAssistant
+      if (messageIndex() < 0) return emptyAssistant

       const result: AssistantMessage[] = []
-      for (let i = index + 1; i < messages.length; i++) {
+      for (let i = 0; i < messages.length; i++) {
         const item = messages[i]
         if (!item) continue
-        if (item.role === "user") break
         if (item.role === "assistant" && item.parentID === msg.id) result.push(item as AssistantMessage)
       }
       return result
PATCH

echo "solve.sh: patch applied"
