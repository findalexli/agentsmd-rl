#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-/workspace/openclaw}"
FILE="$REPO/extensions/msteams/src/monitor-handler/message-handler.ts"

# Idempotency: check if the fix is already applied
if grep -q 'groupPolicy === "allowlist"' "$FILE" 2>/dev/null && \
   grep -A5 'groupPolicy === "allowlist"' "$FILE" | grep -q 'resolveMSTeamsAllowlistMatch' 2>/dev/null; then
  # Need to distinguish the existing usage from the new thread-filter usage.
  # The fix adds filtering right after allMessages is built, before formatThreadContext.
  if grep -B2 'formatThreadContext' "$FILE" | grep -q 'threadMessages\|allMessages.filter'; then
    echo "Fix already applied."
    exit 0
  fi
fi

cd "$REPO"

git apply - <<'PATCH'
diff --git a/extensions/msteams/src/monitor-handler/message-handler.ts b/extensions/msteams/src/monitor-handler/message-handler.ts
index 3a74136b0132..f96468740920 100644
--- a/extensions/msteams/src/monitor-handler/message-handler.ts
+++ b/extensions/msteams/src/monitor-handler/message-handler.ts
@@ -459,7 +459,18 @@ export function createMSTeamsMessageHandler(deps: MSTeamsMessageHandlerDeps) {
           fetchThreadReplies(graphToken, groupId, conversationId, activity.replyToId),
         ]);
         const allMessages = parentMsg ? [parentMsg, ...replies] : replies;
-        const formatted = formatThreadContext(allMessages, activity.id);
+        const threadMessages =
+          groupPolicy === "allowlist"
+            ? allMessages.filter((msg) => {
+                return resolveMSTeamsAllowlistMatch({
+                  allowFrom: effectiveGroupAllowFrom,
+                  senderId: msg.from?.user?.id ?? "",
+                  senderName: msg.from?.user?.displayName,
+                  allowNameMatching,
+                }).allowed;
+              })
+            : allMessages;
+        const formatted = formatThreadContext(threadMessages, activity.id);
         if (formatted) {
           threadContext = formatted;
         }

PATCH

echo "Patch applied successfully."
