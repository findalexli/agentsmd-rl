#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'isMessageInterrupted' src/features/Conversation/store/slices/messageState/selectors.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/.agents/skills/electron-testing/SKILL.md b/.agents/skills/electron-testing/SKILL.md
index 184fd95bd31..373a144df4d 100644
--- a/.agents/skills/electron-testing/SKILL.md
+++ b/.agents/skills/electron-testing/SKILL.md
@@ -203,6 +203,59 @@ EVALEOF
 agent-browser --cdp 9222 eval "JSON.stringify(window.__CAPTURED_ERRORS)"
 ```
 
+## Screen Recording
+
+Record automated demos by combining `ffmpeg` screen capture with `agent-browser` automation. The script `.agents/skills/electron-testing/record-electron-demo.sh` handles the full lifecycle.
+
+### Usage
+
+```bash
+# Run the built-in demo (queue-edit feature)
+./.agents/skills/electron-testing/record-electron-demo.sh
+
+# Run a custom automation script
+./.agents/skills/electron-testing/record-electron-demo.sh ./my-demo.sh /tmp/my-demo.mp4
+```
+
+The script automatically:
+
+1. Starts Electron with CDP and waits for SPA to load
+2. Detects the window position, screen, and Retina scale via Swift/CGWindowList
+3. Records only the Electron window region using `ffmpeg -f avfoundation` with crop
+4. Runs the demo (built-in or custom script receiving CDP port as `$1`)
+5. Stops recording and cleans up
+
+### Writing Custom Demo Scripts
+
+Create a shell script that receives the CDP port as `$1`:
+
+```bash
+#!/usr/bin/env bash
+# my-demo.sh — Custom demo script
+PORT=$1
+
+# Navigate
+agent-browser --cdp "$PORT" snapshot -i 2>&1 | grep 'link "Lobe AI"'
+agent-browser --cdp "$PORT" click @e34
+sleep 3
+
+# Find input and type
+INPUT=$(agent-browser --cdp "$PORT" snapshot -i -C 2>&1 \
+  | grep "editable" | grep -oE 'ref=e[0-9]+' | head -1 | sed 's/ref=//')
+agent-browser --cdp "$PORT" click "@$INPUT"
+agent-browser --cdp "$PORT" type "@$INPUT" "Hello world"
+agent-browser --cdp "$PORT" press Enter
+sleep 5
+```
+
+### Key Details
+
+- **Multi-monitor support**: Uses Swift to find which screen the Electron window is on and calculates relative crop coordinates
+- **Retina aware**: Scales crop coordinates by the display's `backingScaleFactor`
+- **No window resize**: Records the window at its current position/size to avoid triggering SPA reload
+- **SPA load polling**: Waits for interactive elements to appear before starting the demo
+- **Prerequisites**: `ffmpeg` (`brew install ffmpeg`), `agent-browser`
+
 ## Gotchas
 
 - **`npx electron-vite dev` must run from `apps/desktop/`** — running from project root fails silently
@@ -213,3 +266,5 @@ agent-browser --cdp 9222 eval "JSON.stringify(window.__CAPTURED_ERRORS)"
 - **`fill` doesn't work on contenteditable** — use `type` for the chat input
 - **Screenshots go to `~/.agent-browser/tmp/screenshots/`** — read them with the `Read` tool
 - **Store is at `window.__LOBE_STORES`** not `window.__ZUSTAND_STORES__` — use `.chat()` to get current state
+- **Don't resize the Electron window after load** — resizing triggers a full SPA reload (splash screen), which can take 30+ seconds or get stuck. Record at the window's current size instead
+- **`screencapture -V -l<windowid>`** doesn't work reliably for video — use `ffmpeg -f avfoundation` with crop instead (see Screen Recording section)
diff --git a/.agents/skills/electron-testing/record-electron-demo.sh b/.agents/skills/electron-testing/record-electron-demo.sh
new file mode 100755
index 00000000000..d5f1a6fd336
--- /dev/null
+++ b/.agents/skills/electron-testing/record-electron-demo.sh
@@ -0,0 +1,353 @@
+#!/usr/bin/env bash
+#
+# record-electron-demo.sh — Record an automated demo of the Electron app
+#
+# Usage:
+#   ./scripts/record-electron-demo.sh [script.sh] [output.mp4]
+#
+#   script.sh  — A shell script containing agent-browser commands to automate.
+#                It receives the CDP port as $1. Defaults to a built-in queue-edit demo.
+#   output.mp4 — Output file path. Defaults to /tmp/electron-demo.mp4
+#
+# Prerequisites:
+#   - agent-browser CLI installed globally
+#   - ffmpeg installed (brew install ffmpeg)
+#   - Electron app NOT already running (script manages lifecycle)
+#
+# Examples:
+#   # Run built-in demo
+#   ./scripts/record-electron-demo.sh
+#
+#   # Run custom automation script
+#   ./scripts/record-electron-demo.sh ./my-demo.sh /tmp/my-demo.mp4
+#
+set -euo pipefail
+
+CDP_PORT=9222
+DEMO_SCRIPT="${1:-}"
+OUTPUT="${2:-/tmp/electron-demo.mp4}"
+ELECTRON_LOG="/tmp/electron-dev.log"
+SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
+PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
+RECORD_PID=""
+
+# ── Helpers ──────────────────────────────────────────────────────────
+
+cleanup() {
+  echo "[cleanup] Stopping all processes..."
+  [ -n "$RECORD_PID" ] && kill -INT "$RECORD_PID" 2>/dev/null && sleep 2
+  pkill -f "electron-vite" 2>/dev/null || true
+  pkill -f "Electron" 2>/dev/null || true
+  pkill -f "agent-browser" 2>/dev/null || true
+  echo "[cleanup] Done."
+}
+trap cleanup EXIT
+
+wait_for_electron() {
+  echo "[wait] Waiting for Electron to start..."
+  for i in $(seq 1 24); do
+    sleep 5
+    if strings "$ELECTRON_LOG" 2>/dev/null | grep -q "starting electron"; then
+      echo "[wait] Electron process ready."
+      return 0
+    fi
+    echo "[wait] Still waiting... (${i}/24)"
+  done
+  echo "[error] Electron failed to start within 120s"
+  exit 1
+}
+
+wait_for_renderer() {
+  echo "[wait] Waiting for renderer to load..."
+  sleep 15
+  agent-browser --cdp "$CDP_PORT" wait 3000
+
+  # Poll until interactive elements appear (SPA may take extra time)
+  for i in $(seq 1 12); do
+    local snap
+    snap=$(agent-browser --cdp "$CDP_PORT" snapshot -i 2>&1)
+    if echo "$snap" | grep -q 'link "'; then
+      echo "[wait] Renderer ready (interactive elements found)."
+      return 0
+    fi
+    echo "[wait] SPA still loading... (${i}/12)"
+    sleep 5
+  done
+  echo "[warn] Timed out waiting for interactive elements, proceeding anyway."
+}
+
+get_window_and_screen_info() {
+  # Returns: window_x window_y window_w window_h screen_index
+  # Uses Swift to find the Electron window bounds and which screen it's on
+  swift -e '
+    import Cocoa
+    let windowList = CGWindowListCopyWindowInfo([.optionAll], kCGNullWindowID) as! [[String: Any]]
+    for w in windowList {
+      let owner = w["kCGWindowOwnerName"] as? String ?? ""
+      let name = w["kCGWindowName"] as? String ?? ""
+      let layer = w["kCGWindowLayer"] as? Int ?? -1
+      let bounds = w["kCGWindowBounds"] as? [String: Any] ?? [:]
+      let wx = bounds["X"] as? Double ?? 0
+      let wy = bounds["Y"] as? Double ?? 0
+      let ww = bounds["Width"] as? Double ?? 0
+      let wh = bounds["Height"] as? Double ?? 0
+      if (owner == "Electron" || owner == "LobeHub") && layer == 0 && name == "LobeHub" && ww > 200 && wh > 200 {
+        // Find which screen this window is on
+        let screens = NSScreen.screens
+        var screenIdx = 0
+        let windowCenter = NSPoint(x: wx + ww / 2, y: wy + wh / 2)
+        for (i, screen) in screens.enumerated() {
+          let frame = screen.frame
+          // Convert CG coords (top-left origin) to NSScreen coords (bottom-left origin)
+          let mainHeight = screens[0].frame.height
+          let screenTop = mainHeight - frame.origin.y - frame.height
+          let screenBottom = screenTop + frame.height
+          let screenLeft = frame.origin.x
+          let screenRight = screenLeft + frame.width
+          if windowCenter.x >= screenLeft && windowCenter.x <= screenRight &&
+             windowCenter.y >= screenTop && windowCenter.y <= screenBottom {
+            screenIdx = i
+            break
+          }
+        }
+        // Compute window position relative to the screen it is on
+        let screen = screens[screenIdx]
+        let mainHeight = screens[0].frame.height
+        let screenTop = mainHeight - screen.frame.origin.y - screen.frame.height
+        let relX = wx - screen.frame.origin.x
+        let relY = wy - screenTop
+        let scale = Int(screen.backingScaleFactor)
+        print("\(Int(relX)) \(Int(relY)) \(Int(ww)) \(Int(wh)) \(screenIdx) \(scale)")
+        break
+      }
+    }
+  '
+}
+
+start_recording() {
+  local rel_x=$1 rel_y=$2 w=$3 h=$4 screen_idx=$5 scale=$6
+
+  # ffmpeg avfoundation device index for screens
+  # List devices and find the one matching our screen index
+  local device_idx
+  device_idx=$(ffmpeg -f avfoundation -list_devices true -i "" 2>&1 \
+    | grep "Capture screen ${screen_idx}" \
+    | grep -oE '\[[0-9]+\]' | tr -d '[]' || true)
+
+  if [ -z "$device_idx" ]; then
+    echo "[warn] Could not find capture device for screen $screen_idx, trying default (3)"
+    device_idx=3
+  fi
+
+  # Scale coordinates to native resolution
+  local cx=$((rel_x * scale))
+  local cy=$((rel_y * scale))
+  local cw=$((w * scale))
+  local ch=$((h * scale))
+
+  echo "[record] Window: ${rel_x},${rel_y} ${w}x${h} on screen ${screen_idx} (scale=${scale})"
+  echo "[record] Crop: ${cx},${cy} ${cw}x${ch}, device: ${device_idx}"
+  echo "[record] Output: $OUTPUT"
+
+  ffmpeg -y \
+    -f avfoundation -framerate 30 -capture_cursor 1 -i "${device_idx}:" \
+    -vf "crop=${cw}:${ch}:${cx}:${cy},scale=${w}:${h}" \
+    -c:v libx264 -crf 23 -preset fast -an \
+    "$OUTPUT" \
+    > /tmp/ffmpeg-record.log 2>&1 &
+  RECORD_PID=$!
+  sleep 2
+
+  if ! kill -0 "$RECORD_PID" 2>/dev/null; then
+    echo "[error] ffmpeg failed to start. Log:"
+    cat /tmp/ffmpeg-record.log
+    RECORD_PID=""
+    return 1
+  fi
+  echo "[record] Recording started (PID=$RECORD_PID)"
+}
+
+stop_recording() {
+  if [ -n "$RECORD_PID" ]; then
+    echo "[record] Stopping recording..."
+    kill -INT "$RECORD_PID" 2>/dev/null || true
+    wait "$RECORD_PID" 2>/dev/null || true
+    RECORD_PID=""
+    echo "[record] Saved to $OUTPUT"
+    ls -lh "$OUTPUT"
+  fi
+}
+
+# ── Built-in demo: Queue Edit ────────────────────────────────────────
+
+find_input_ref() {
+  local port=$1
+  agent-browser --cdp "$port" snapshot -i -C 2>&1 \
+    | grep "editable" \
+    | grep -oE 'ref=e[0-9]+' \
+    | head -1 \
+    | sed 's/ref=//'
+}
+
+builtin_demo() {
+  local port=$1
+
+  echo "[demo] Step 1: Navigate to first available agent"
+  local snapshot agent_ref
+  snapshot=$(agent-browser --cdp "$port" snapshot -i 2>&1)
+  # Try Lobe AI first, then fall back to any agent link in the sidebar
+  agent_ref=$(echo "$snapshot" | grep -oE 'link "Lobe AI" \[ref=e[0-9]+\]' | grep -oE 'e[0-9]+' || true)
+  if [ -z "$agent_ref" ]; then
+    # Pick the first agent-like link (skip nav links)
+    agent_ref=$(echo "$snapshot" | grep 'link "' | grep -vE '"Home"|"Pages"|"Settings"|"Search"|"Resources"|"Marketplace"' | head -1 | grep -oE 'ref=e[0-9]+' | sed 's/ref=//' || true)
+  fi
+  if [ -z "$agent_ref" ]; then
+    echo "[error] No agent link found in snapshot"
+    echo "$snapshot" | head -30
+    return 1
+  fi
+  echo "[demo] Clicking agent ref: @$agent_ref"
+  agent-browser --cdp "$port" click "@$agent_ref"
+  sleep 3
+
+  echo "[demo] Step 2: Send first message (triggers AI generation)"
+  local input_ref
+  input_ref=$(find_input_ref "$port")
+  agent-browser --cdp "$port" click "@$input_ref"
+  agent-browser --cdp "$port" type "@$input_ref" "Write a 3000 word essay about the complete history of space exploration from Sputnik to the James Webb Space Telescope"
+  sleep 1
+  agent-browser --cdp "$port" press Enter
+  sleep 3
+
+  echo "[demo] Step 3: Queue message 1"
+  input_ref=$(find_input_ref "$port")
+  agent-browser --cdp "$port" click "@$input_ref"
+  agent-browser --cdp "$port" type "@$input_ref" "This message should be edited"
+  sleep 1
+  agent-browser --cdp "$port" press Enter
+  sleep 1
+
+  echo "[demo] Step 4: Queue message 2"
+  input_ref=$(find_input_ref "$port")
+  agent-browser --cdp "$port" click "@$input_ref"
+  agent-browser --cdp "$port" type "@$input_ref" "Another queued message"
+  sleep 1
+  agent-browser --cdp "$port" press Enter
+  sleep 1
+
+  echo "[demo] Step 5: Verify queue has messages"
+  local queue_count
+  queue_count=$(agent-browser --cdp "$port" eval --stdin << 'EVALEOF'
+(function() {
+  var chat = window.__LOBE_STORES.chat();
+  var total = 0;
+  Object.keys(chat.queuedMessages).forEach(function(k) {
+    total += chat.queuedMessages[k].length;
+  });
+  return String(total);
+})()
+EVALEOF
+  )
+  echo "[demo] Queue count: $queue_count"
+
+  if [ "$queue_count" = "0" ] || [ "$queue_count" = '"0"' ]; then
+    echo "[demo] Queue was already drained. Retrying..."
+    input_ref=$(find_input_ref "$port")
+    agent-browser --cdp "$port" click "@$input_ref"
+    agent-browser --cdp "$port" type "@$input_ref" "Now write another 3000 word essay about artificial intelligence from Turing to transformers covering every major breakthrough"
+    sleep 1
+    agent-browser --cdp "$port" press Enter
+    sleep 2
+    input_ref=$(find_input_ref "$port")
+    agent-browser --cdp "$port" click "@$input_ref"
+    agent-browser --cdp "$port" type "@$input_ref" "This message should be edited"
+    sleep 1
+    agent-browser --cdp "$port" press Enter
+    sleep 1
+    input_ref=$(find_input_ref "$port")
+    agent-browser --cdp "$port" click "@$input_ref"
+    agent-browser --cdp "$port" type "@$input_ref" "Another queued message"
+    sleep 1
+    agent-browser --cdp "$port" press Enter
+    sleep 1
+  fi
+
+  echo "[demo] Step 6: Scroll to show queue tray"
+  agent-browser --cdp "$port" scroll down 5000
+  sleep 2
+
+  echo "[demo] Step 7: Click edit button on first queued message"
+  agent-browser --cdp "$port" eval --stdin << 'EVALEOF'
+(function() {
+  var chat = window.__LOBE_STORES.chat();
+  var keys = Object.keys(chat.queuedMessages);
+  for (var k = 0; k < keys.length; k++) {
+    var queue = chat.queuedMessages[keys[k]];
+    if (queue.length > 0) {
+      var targetText = queue[0].content;
+      var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
+      while (walker.nextNode()) {
+        var node = walker.currentNode;
+        if (node.textContent.trim() === targetText) {
+          var row = node.parentElement.parentElement;
+          var buttons = row.querySelectorAll('[role="button"]');
+          if (buttons.length >= 1) {
+            buttons[0].click();
+            return 'clicked edit on: ' + targetText;
+          }
+        }
+      }
+    }
+  }
+  return 'edit button not found';
+})()
+EVALEOF
+  sleep 3
+
+  echo "[demo] Step 8: Show result — content restored to input"
+  sleep 3
+
+  echo "[demo] Complete!"
+}
+
+# ── Main ─────────────────────────────────────────────────────────────
+
+echo "=== Electron Demo Recorder ==="
+
+# 1. Kill existing instances
+echo "[setup] Cleaning up existing processes..."
+pkill -f "Electron" 2>/dev/null || true
+pkill -f "electron-vite" 2>/dev/null || true
+pkill -f "agent-browser" 2>/dev/null || true
+sleep 3
+
+# 2. Start Electron
+echo "[setup] Starting Electron..."
+cd "$PROJECT_ROOT/apps/desktop"
+ELECTRON_ENABLE_LOGGING=1 npx electron-vite dev -- --remote-debugging-port="$CDP_PORT" > "$ELECTRON_LOG" 2>&1 &
+
+wait_for_electron
+wait_for_renderer
+
+# 3. Get window position and start recording
+WIN_INFO=$(get_window_and_screen_info)
+if [ -z "$WIN_INFO" ]; then
+  echo "[error] Could not find Electron window"
+  exit 1
+fi
+read -r WIN_X WIN_Y WIN_W WIN_H SCREEN_IDX SCALE <<< "$WIN_INFO"
+start_recording "$WIN_X" "$WIN_Y" "$WIN_W" "$WIN_H" "$SCREEN_IDX" "$SCALE"
+
+# 4. Run demo script
+if [ -n "$DEMO_SCRIPT" ] && [ -f "$DEMO_SCRIPT" ]; then
+  echo "[demo] Running custom script: $DEMO_SCRIPT"
+  bash "$DEMO_SCRIPT" "$CDP_PORT"
+else
+  echo "[demo] Running built-in queue-edit demo"
+  builtin_demo "$CDP_PORT"
+fi
+
+# 5. Stop recording
+stop_recording
+
+echo "=== Done! Output: $OUTPUT ==="
diff --git a/locales/en-US/chat.json b/locales/en-US/chat.json
index 1e8d94b1599..211b8ec3aaf 100644
--- a/locales/en-US/chat.json
+++ b/locales/en-US/chat.json
@@ -175,6 +175,8 @@
   "messageAction.delAndRegenerate": "Delete and Regenerate",
   "messageAction.deleteDisabledByThreads": "This message has a subtopic and can’t be deleted",
   "messageAction.expand": "Expand Message",
+  "messageAction.interrupted": "Interrupted",
+  "messageAction.interruptedHint": "What should I do instead?",
   "messageAction.reaction": "Add Reaction",
   "messageAction.regenerate": "Regenerate",
   "messages.dm.sentTo": "Visible only to {{name}}",
diff --git a/locales/zh-CN/chat.json b/locales/zh-CN/chat.json
index 886ae87982f..e0f5696826a 100644
--- a/locales/zh-CN/chat.json
+++ b/locales/zh-CN/chat.json
@@ -175,6 +175,8 @@
   "messageAction.delAndRegenerate": "删除并重新生成",
   "messageAction.deleteDisabledByThreads": "该消息有子话题，无法删除",
   "messageAction.expand": "展开消息",
+  "messageAction.interrupted": "已中断",
+  "messageAction.interruptedHint": "接下来需要做什么？",
   "messageAction.reaction": "添加表情",
   "messageAction.regenerate": "重新生成",
   "messages.dm.sentTo": "仅对 {{name}} 可见",
diff --git a/src/features/Conversation/ChatInput/QueueTray.tsx b/src/features/Conversation/ChatInput/QueueTray.tsx
index 2e7d3ae2719..84777d6bd39 100644
--- a/src/features/Conversation/ChatInput/QueueTray.tsx
+++ b/src/features/Conversation/ChatInput/QueueTray.tsx
@@ -2,8 +2,8 @@
 
 import { ActionIcon, Flexbox, Icon } from '@lobehub/ui';
 import { createStaticStyles } from 'antd-style';
-import { ListEnd, Trash2 } from 'lucide-react';
-import { memo, useMemo } from 'react';
+import { ListEnd, Pencil, Trash2 } from 'lucide-react';
+import { memo, useCallback, useMemo } from 'react';
 
 import { useChatStore } from '@/store/chat';
 import { operationSelectors } from '@/store/chat/selectors';
@@ -54,6 +54,16 @@ const QueueTray = memo(() => {
 
   const queuedMessages = useChatStore((s) => operationSelectors.getQueuedMessages(context)(s));
   const removeQueuedMessage = useChatStore((s) => s.removeQueuedMessage);
+  const editor = useConversationStore((s) => s.editor);
+
+  const handleEdit = useCallback(
+    (msgId: string, content: string) => {
+      removeQueuedMessage(contextKey, msgId);
+      editor?.setDocument('markdown', content);
+      editor?.focus();
+    },
+    [contextKey, editor, removeQueuedMessage],
+  );
 
   if (queuedMessages.length === 0) return null;
 
@@ -71,6 +81,7 @@ const QueueTray = memo(() => {
           <Flexbox className={styles.text} flex={1}>
             {msg.content}
           </Flexbox>
+          <ActionIcon icon={Pencil} size="small" onClick={() => handleEdit(msg.id, msg.content)} />
           <ActionIcon
             icon={Trash2}
             size="small"
diff --git a/src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx b/src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx
new file mode 100644
index 00000000000..1a98508cb7d
--- /dev/null
+++ b/src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx
@@ -0,0 +1,25 @@
+import { createStaticStyles } from 'antd-style';
+import { memo } from 'react';
+import { useTranslation } from 'react-i18next';
+
+const styles = createStaticStyles(({ css, cssVar }) => ({
+  container: css`
+    padding-block: 4px;
+    font-size: 12px;
+    color: ${cssVar.colorTextTertiary};
+  `,
+}));
+
+const InterruptedHint = memo(() => {
+  const { t } = useTranslation('chat');
+
+  return (
+    <div className={styles.container}>
+      {t('messageAction.interrupted')} · {t('messageAction.interruptedHint')}
+    </div>
+  );
+});
+
+InterruptedHint.displayName = 'InterruptedHint';
+
+export default InterruptedHint;
diff --git a/src/features/Conversation/Messages/Assistant/index.tsx b/src/features/Conversation/Messages/Assistant/index.tsx
index fb22daa4f8e..fb592e68422 100644
--- a/src/features/Conversation/Messages/Assistant/index.tsx
+++ b/src/features/Conversation/Messages/Assistant/index.tsx
@@ -19,6 +19,7 @@ import {
   useSetMessageItemActionElementPortialContext,
   useSetMessageItemActionTypeContext,
 } from '../Contexts/message-action-context';
+import InterruptedHint from './components/InterruptedHint';
 import MessageContent from './components/MessageContent';
 import { AssistantMessageExtra } from './Extra';
 
@@ -55,9 +56,10 @@ const AssistantMessage = memo<AssistantMessageProps>(({ id, index, disableEditin
 
   const avatar = useAgentMeta(agentId);
 
-  // Get editing and generating state from ConversationStore
+  // Get editing, generating, and interrupted state from ConversationStore
   const editing = useConversationStore(messageStateSelectors.isMessageEditing(id));
   const generating = useConversationStore(messageStateSelectors.isMessageGenerating(id));
+  const interrupted = useConversationStore(messageStateSelectors.isMessageInterrupted(id));
 
   const errorContent = useErrorContent(error);
 
@@ -116,16 +118,19 @@ const AssistantMessage = memo<AssistantMessageProps>(({ id, index, disableEditin
           : undefined
       }
       messageExtra={
-        <AssistantMessageExtra
-          content={content}
-          extra={extra}
-          id={id}
-          model={model!}
-          performance={performance! || metadata}
-          provider={provider!}
-          tools={tools}
-          usage={usage! || metadata}
-        />
+        <>
+          {interrupted && <InterruptedHint />}
+          <AssistantMessageExtra
+            content={content}
+            extra={extra}
+            id={id}
+            model={model!}
+            performance={performance! || metadata}
+            provider={provider!}
+            tools={tools}
+            usage={usage! || metadata}
+          />
+        </>
       }
       onDoubleClick={onDoubleClick}
       onMouseEnter={onMouseEnter}
diff --git a/src/features/Conversation/Messages/AssistantGroup/index.tsx b/src/features/Conversation/Messages/AssistantGroup/index.tsx
index e84b525fb3d..352be0f78c4 100644
--- a/src/features/Conversation/Messages/AssistantGroup/index.tsx
+++ b/src/features/Conversation/Messages/AssistantGroup/index.tsx
@@ -18,6 +18,7 @@ import { userGeneralSettingsSelectors, userProfileSelectors } from '@/store/user
 import { ReactionDisplay } from '../../components/Reaction';
 import { useAgentMeta } from '../../hooks';
 import { dataSelectors, messageStateSelectors, useConversationStore } from '../../store';
+import InterruptedHint from '../Assistant/components/InterruptedHint';
 import Usage from '../components/Extras/Usage';
 import MessageBranch from '../components/MessageBranch';
 import {
@@ -69,8 +70,16 @@ const GroupMessage = memo<GroupMessageProps>(({ id, index, disableEditing }) =>
 
   const contentId = lastAssistantMsg?.id;
 
-  // Get editing state from ConversationStore
+  // Get editing and interrupted state from ConversationStore
   const editing = useConversationStore(messageStateSelectors.isMessageEditing(contentId || ''));
+  // Check interrupted on both the group root and the active block, because
+  // continuation runs attach their operations to lastBlockId (contentId),
+  // not the group root.
+  const groupInterrupted = useConversationStore(messageStateSelectors.isMessageInterrupted(id));
+  const blockInterrupted = useConversationStore(
+    messageStateSelectors.isMessageInterrupted(contentId || ''),
+  );
+  const interrupted = groupInterrupted || blockInterrupted;
 
   const isDevMode = useUserStore((s) => userGeneralSettingsSelectors.config(s).isDevMode);
   const addReaction = useConversationStore((s) => s.addReaction);
@@ -162,6 +171,7 @@ const GroupMessage = memo<GroupMessageProps>(({ id, index, disableEditing }) =>
           <FileListViewer items={aggregatedFileList} />
         </div>
       )}
+      {interrupted && <InterruptedHint />}
       {isDevMode && model && (
         <Usage model={model} performance={performance} provider={provider!} usage={usage} />
       )}
diff --git a/src/features/Conversation/store/slices/messageState/selectors.ts b/src/features/Conversation/store/slices/messageState/selectors.ts
index ffb999ee9f7..49e3fb9fb8b 100644
--- a/src/features/Conversation/store/slices/messageState/selectors.ts
+++ b/src/features/Conversation/store/slices/messageState/selectors.ts
@@ -75,6 +75,12 @@ const isMessageRegenerating = (id: string) => (s: State) =>
 const isMessageContinuing = (id: string) => (s: State) =>
   s.operationState.getMessageOperationState(id).isContinuing;
 
+/**
+ * Check if a message generation was interrupted by user
+ */
+const isMessageInterrupted = (id: string) => (s: State) =>
+  s.operationState.getMessageOperationState(id).isInterrupted;
+
 /**
  * Check if a message is in reasoning state
  */
@@ -150,6 +156,7 @@ export const messageStateSelectors = {
   isMessageEditing,
   isMessageGenerating,
   isMessageInReasoning,
+  isMessageInterrupted,
   isMessageLoading,
   isMessageProcessing,
   isMessageRegenerating,
diff --git a/src/features/Conversation/types/operation.ts b/src/features/Conversation/types/operation.ts
index a6b6745d7e9..e4ec259d4f9 100644
--- a/src/features/Conversation/types/operation.ts
+++ b/src/features/Conversation/types/operation.ts
@@ -25,6 +25,11 @@ export interface MessageOperationState {
    */
   isInReasoning: boolean;
 
+  /**
+   * Message generation was interrupted by user
+   */
+  isInterrupted: boolean;
+
   /**
    * Message has any operation in progress
    */
@@ -106,6 +111,7 @@ export const DEFAULT_MESSAGE_OPERATION_STATE: MessageOperationState = {
   isCreating: false,
   isGenerating: false,
   isInReasoning: false,
+  isInterrupted: false,
   isProcessing: false,
   isRegenerating: false,
 };
diff --git a/src/hooks/useOperationState.ts b/src/hooks/useOperationState.ts
index d3decb16d33..91f21563ee3 100644
--- a/src/hooks/useOperationState.ts
+++ b/src/hooks/useOperationState.ts
@@ -73,14 +73,25 @@ export const useOperationState = (context: ConversationContext): OperationState
         const messageOps = operationIds.map((id) => operations[id]).filter(Boolean);
         const runningOps = messageOps.filter((op) => op.status === 'running');
 
+        const isGenerating = runningOps.some((op) => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
+
+        // A message is interrupted only if the latest AI runtime operation was cancelled.
+        // Using .some() would incorrectly flag messages where a stale cancelled op
+        // precedes a successful retry (stop-then-continue flow).
+        const latestRuntimeOp = [...messageOps]
+          .reverse()
+          .find((op) => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
+        const isInterrupted =
+          !isGenerating && !!latestRuntimeOp && latestRuntimeOp.status === 'cancelled';
+
         return {
           isContinuing: runningOps.some((op) => op.type === 'continue'),
           isCreating: runningOps.some(
             (op) => op.type === 'sendMessage' || op.type === 'createAssistantMessage',
           ),
-          // Check AI runtime operations (client-side and server-side)
-          isGenerating: runningOps.some((op) => AI_RUNTIME_OPERATION_TYPES.includes(op.type)),
+          isGenerating,
           isInReasoning: runningOps.some((op) => op.type === 'reasoning'),
+          isInterrupted,
           isProcessing: operationSelectors.isMessageProcessing(messageId)(state),
           isRegenerating: runningOps.some((op) => op.type === 'regenerate'),
         };
diff --git a/src/locales/default/chat.ts b/src/locales/default/chat.ts
index 9ed9524c022..344b85d6841 100644
--- a/src/locales/default/chat.ts
+++ b/src/locales/default/chat.ts
@@ -188,6 +188,8 @@ export default {
   'messageAction.collapse': 'Collapse Message',
   'messageAction.continueGeneration': 'Continue Generating',
   'messageAction.delAndRegenerate': 'Delete and Regenerate',
+  'messageAction.interrupted': 'Interrupted',
+  'messageAction.interruptedHint': 'What should I do instead?',
   'messageAction.deleteDisabledByThreads': 'This message has a subtopic and can’t be deleted',
   'messageAction.expand': 'Expand Message',
   'messageAction.reaction': 'Add Reaction',
diff --git a/src/store/chat/slices/aiChat/actions/__tests__/streamingExecutor.test.ts b/src/store/chat/slices/aiChat/actions/__tests__/streamingExecutor.test.ts
index 4f1785e5983..178142473a0 100644
--- a/src/store/chat/slices/aiChat/actions/__tests__/streamingExecutor.test.ts
+++ b/src/store/chat/slices/aiChat/actions/__tests__/streamingExecutor.test.ts
@@ -278,10 +278,11 @@ describe('StreamingExecutor actions', () => {
       // Verify only one LLM call was made (no tool execution happened)
       expect(streamCallCount).toBe(1);
 
-      // Verify the agent runtime completed (not just cancelled mid-flight)
+      // Verify the operation preserves cancelled status (user intentionally stopped it)
+      // even though tools were gracefully resolved after cancellation
       const operations = Object.values(result.current.operations);
       const execOperation = operations.find((op) => op.type === 'execAgentRuntime');
-      expect(execOperation?.status).toBe('completed');
+      expect(execOperation?.status).toBe('cancelled');
 
       streamSpy.mockRestore();
     });
diff --git a/src/store/chat/slices/operation/actions.ts b/src/store/chat/slices/operation/actions.ts
index c78e1275472..4edafe3d19d 100644
--- a/src/store/chat/slices/operation/actions.ts
+++ b/src/store/chat/slices/operation/actions.ts
@@ -272,7 +272,12 @@ export class OperationActionsImpl {
         if (!operation) return;
 
         const now = Date.now();
-        operation.status = 'completed';
+
+        // Don't override cancelled status - preserve user interruption state
+        if (operation.status !== 'cancelled') {
+          operation.status = 'completed';
+        }
+
         operation.metadata.endTime = now;
         operation.metadata.duration = now - operation.metadata.startTime;
 

PATCH

echo "Patch applied successfully."
