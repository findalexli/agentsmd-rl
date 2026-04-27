#!/usr/bin/env bash
set -euo pipefail

cd /workspace/OpenHands

# Idempotency: bail out if the gold change is already applied.
if [ -f frontend/src/utils/browser-tab.ts ] && \
   grep -q "Alternate between the latest baseline title and the notification message" \
        frontend/src/utils/browser-tab.ts 2>/dev/null; then
    echo "Gold solution already applied; skipping."
    exit 0
fi

# Apply the gold patch. The diff is inlined here; we do NOT fetch from GitHub.
# Note: the test files (.test.ts) and notification.mp3 from the original PR are
# NOT part of the agent's contract — they live in the verifier image and the
# test harness, respectively. The patch below contains only the source-code
# changes the agent is expected to make.
git apply --whitespace=nowarn <<'PATCH'
diff --git a/frontend/src/components/features/controls/agent-status.tsx b/frontend/src/components/features/controls/agent-status.tsx
index b0dba1fa25cd..176bffea234f 100644
--- a/frontend/src/components/features/controls/agent-status.tsx
+++ b/frontend/src/components/features/controls/agent-status.tsx
@@ -14,6 +14,7 @@ import { useAgentState } from "#/hooks/use-agent-state";
 import { useUnifiedWebSocketStatus } from "#/hooks/use-unified-websocket-status";
 import { useTaskPolling } from "#/hooks/query/use-task-polling";
 import { useSubConversationTaskPolling } from "#/hooks/query/use-sub-conversation-task-polling";
+import { useAgentNotification } from "#/hooks/use-agent-notification";

 export interface AgentStatusProps {
   className?: string;
@@ -33,6 +34,9 @@ export function AgentStatus({
   const { t } = useTranslation();
   const { setShouldShownAgentLoading } = useConversationStore();
   const { curAgentState, executionStatus } = useAgentState();
+
+  // Trigger browser tab flash and notification sound on state changes
+  useAgentNotification(curAgentState);
   const webSocketStatus = useUnifiedWebSocketStatus();
   const { data: conversation } = useActiveConversation();
   const { taskStatus } = useTaskPolling();
diff --git a/frontend/src/hooks/use-agent-notification.ts b/frontend/src/hooks/use-agent-notification.ts
new file mode 100644
index 000000000000..bef6190811eb
--- /dev/null
+++ b/frontend/src/hooks/use-agent-notification.ts
@@ -0,0 +1,76 @@
+import { useEffect, useRef } from "react";
+import { useTranslation } from "react-i18next";
+import { AgentState } from "#/types/agent-state";
+import { browserTab } from "#/utils/browser-tab";
+import { useSettings } from "#/hooks/query/use-settings";
+import { AGENT_STATUS_MAP } from "#/utils/status";
+import notificationSound from "#/assets/notification.mp3";
+
+const NOTIFICATION_STATES: AgentState[] = [
+  AgentState.AWAITING_USER_INPUT,
+  AgentState.FINISHED,
+  AgentState.AWAITING_USER_CONFIRMATION,
+];
+
+/**
+ * Hook that triggers browser tab flashing and notification sound
+ * when the agent transitions into a state that requires user attention.
+ *
+ * - Flashes the browser tab title when the tab is not focused.
+ * - Plays a notification sound if enabled in settings.
+ * - Stops flashing when the user focuses the tab.
+ */
+export function useAgentNotification(curAgentState: AgentState) {
+  const { data: settings } = useSettings();
+  const { t } = useTranslation();
+  const audioRef = useRef<HTMLAudioElement | undefined>(undefined);
+  const prevStateRef = useRef<AgentState | undefined>(undefined);
+
+  // Initialize audio only in browser environment, inside useEffect to
+  // avoid side effects during render (React 18 strict mode, SSR safety).
+  useEffect(() => {
+    if (typeof window !== "undefined" && !audioRef.current) {
+      audioRef.current = new Audio(notificationSound);
+      audioRef.current.volume = 0.5;
+    }
+  }, []);
+
+  const isSoundEnabled = settings?.enable_sound_notifications ?? false;
+
+  // Trigger notification only on actual state transitions into a
+  // notification-worthy state — not when unrelated deps (e.g. settings) change.
+  useEffect(() => {
+    if (prevStateRef.current === curAgentState) return;
+    prevStateRef.current = curAgentState;
+
+    if (!NOTIFICATION_STATES.includes(curAgentState)) return;
+
+    if (isSoundEnabled && audioRef.current) {
+      audioRef.current.currentTime = 0;
+      audioRef.current.play().catch(() => {
+        // Ignore autoplay errors (browsers may block autoplay)
+      });
+    }
+
+    if (typeof document !== "undefined" && !document.hasFocus()) {
+      const i18nKey = AGENT_STATUS_MAP[curAgentState];
+      const message = i18nKey ? t(i18nKey) : curAgentState;
+      browserTab.startNotification(message);
+    }
+  }, [curAgentState, isSoundEnabled, t]);
+
+  // Stop tab notification when window gains focus
+  useEffect(() => {
+    if (typeof window === "undefined") return undefined;
+
+    const handleFocus = () => {
+      browserTab.stopNotification();
+    };
+
+    window.addEventListener("focus", handleFocus);
+    return () => {
+      window.removeEventListener("focus", handleFocus);
+      browserTab.stopNotification();
+    };
+  }, []);
+}
diff --git a/frontend/src/utils/browser-tab.ts b/frontend/src/utils/browser-tab.ts
new file mode 100644
index 000000000000..f08d9656ee71
--- /dev/null
+++ b/frontend/src/utils/browser-tab.ts
@@ -0,0 +1,42 @@
+let originalTitle = "";
+let titleInterval: number | undefined;
+
+const isBrowser =
+  typeof window !== "undefined" && typeof document !== "undefined";
+
+export const browserTab = {
+  startNotification(message: string) {
+    if (!isBrowser) return;
+
+    // Always capture the current title as the baseline to restore to
+    originalTitle = document.title;
+
+    // Clear any existing interval
+    if (titleInterval) {
+      this.stopNotification();
+    }
+
+    // Alternate between the latest baseline title and the notification message.
+    // If the title changes externally (e.g., user renames conversation),
+    // update the baseline so we restore to the new value when stopping.
+    titleInterval = window.setInterval(() => {
+      const current = document.title;
+      if (current !== originalTitle && current !== message) {
+        originalTitle = current;
+      }
+      document.title = current === message ? originalTitle : message;
+    }, 1000);
+  },
+
+  stopNotification() {
+    if (!isBrowser) return;
+
+    if (titleInterval) {
+      window.clearInterval(titleInterval);
+      titleInterval = undefined;
+    }
+    if (originalTitle) {
+      document.title = originalTitle;
+    }
+  },
+};
PATCH

echo "Gold solution applied."
