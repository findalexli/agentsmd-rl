#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if already applied
if grep -q 'Persist.workspace(sdk.directory, "followup"' packages/app/src/pages/session.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/app/src/pages/session.tsx b/packages/app/src/pages/session.tsx
index c41133ded74..752b549b861 100644
--- a/packages/app/src/pages/session.tsx
+++ b/packages/app/src/pages/session.tsx
@@ -57,12 +57,15 @@ import { TerminalPanel } from "@/pages/session/terminal-panel"
 import { useSessionCommands } from "@/pages/session/use-session-commands"
 import { useSessionHashScroll } from "@/pages/session/use-session-hash-scroll"
 import { Identifier } from "@/utils/id"
+import { Persist, persisted } from "@/utils/persist"
 import { extractPromptFromParts } from "@/utils/prompt"
 import { same } from "@/utils/same"
 import { formatServerError } from "@/utils/server-errors"

 const emptyUserMessages: UserMessage[] = []
-const emptyFollowups: (FollowupDraft & { id: string })[] = []
+type FollowupItem = FollowupDraft & { id: string }
+type FollowupEdit = Pick<FollowupItem, "id" | "prompt" | "context">
+const emptyFollowups: FollowupItem[] = []

 type SessionHistoryWindowInput = {
   sessionID: () => string | undefined
@@ -512,15 +515,20 @@ export default function Page() {
     deferRender: false,
   })

-  const [followup, setFollowup] = createStore({
-    items: {} as Record<string, (FollowupDraft & { id: string })[] | undefined>,
-    failed: {} as Record<string, string | undefined>,
-    paused: {} as Record<string, boolean | undefined>,
-    edit: {} as Record<
-      string,
-      { id: string; prompt: FollowupDraft["prompt"]; context: FollowupDraft["context"] } | undefined
-    >,
-  })
+  const [followup, setFollowup] = persisted(
+    Persist.workspace(sdk.directory, "followup", ["followup.v1"]),
+    createStore<{
+      items: Record<string, FollowupItem[] | undefined>
+      failed: Record<string, string | undefined>
+      paused: Record<string, boolean | undefined>
+      edit: Record<string, FollowupEdit | undefined>
+    }>({
+      items: {},
+      failed: {},
+      paused: {},
+      edit: {},
+    }),
+  )

   createComputed((prev) => {
     const key = sessionKey()

PATCH

echo "Patch applied successfully."
