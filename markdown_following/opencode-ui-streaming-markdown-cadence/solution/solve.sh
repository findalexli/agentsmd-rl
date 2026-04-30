#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/opencode"
FILE="$REPO/packages/ui/src/components/message-part.tsx"

# Idempotency: check if already applied
if grep -q 'createPacedValue' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

cd "$REPO"

git apply - <<'PATCH'
diff --git a/packages/ui/src/components/message-part.tsx b/packages/ui/src/components/message-part.tsx
index 8b572aff814..b5baa79b512 100644
--- a/packages/ui/src/components/message-part.tsx
+++ b/packages/ui/src/components/message-part.tsx
@@ -156,37 +156,75 @@ export type PartComponent = Component<MessagePartProps>

 export const PART_MAPPING: Record<string, PartComponent | undefined> = {}

-const TEXT_RENDER_THROTTLE_MS = 100
+const TEXT_RENDER_PACE_MS = 24
+const TEXT_RENDER_SNAP = /[\s.,!?;:)\]]/
+
+function step(size: number) {
+  if (size <= 12) return 2
+  if (size <= 48) return 4
+  if (size <= 96) return 8
+  return Math.min(24, Math.ceil(size / 8))
+}
+
+function next(text: string, start: number) {
+  const end = Math.min(text.length, start + step(text.length - start))
+  const max = Math.min(text.length, end + 8)
+  for (let i = end; i < max; i++) {
+    if (TEXT_RENDER_SNAP.test(text[i] ?? "")) return i + 1
+  }
+  return end
+}

-function createThrottledValue(getValue: () => string) {
+function createPacedValue(getValue: () => string, live?: () => boolean) {
   const [value, setValue] = createSignal(getValue())
+  let shown = getValue()
   let timeout: ReturnType<typeof setTimeout> | undefined
-  let last = 0
+
+  const clear = () => {
+    if (!timeout) return
+    clearTimeout(timeout)
+    timeout = undefined
+  }
+
+  const sync = (text: string) => {
+    shown = text
+    setValue(text)
+  }
+
+  const run = () => {
+    timeout = undefined
+    const text = getValue()
+    if (!live?.()) {
+      sync(text)
+      return
+    }
+    if (!text.startsWith(shown) || text.length <= shown.length) {
+      sync(text)
+      return
+    }
+    const end = next(text, shown.length)
+    sync(text.slice(0, end))
+    if (end < text.length) timeout = setTimeout(run, TEXT_RENDER_PACE_MS)
+  }

   createEffect(() => {
-    const next = getValue()
-    const now = Date.now()
-
-    const remaining = TEXT_RENDER_THROTTLE_MS - (now - last)
-    if (remaining <= 0) {
-      if (timeout) {
-        clearTimeout(timeout)
-        timeout = undefined
-      }
-      last = now
-      setValue(next)
+    const text = getValue()
+    if (!live?.()) {
+      clear()
+      sync(text)
+      return
+    }
+    if (!text.startsWith(shown) || text.length < shown.length) {
+      clear()
+      sync(text)
       return
     }
-    if (timeout) clearTimeout(timeout)
-    timeout = setTimeout(() => {
-      last = Date.now()
-      setValue(next)
-      timeout = undefined
-    }, remaining)
+    if (text.length === shown.length || timeout) return
+    timeout = setTimeout(run, TEXT_RENDER_PACE_MS)
   })

   onCleanup(() => {
-    if (timeout) clearTimeout(timeout)
+    clear()
   })

   return value
@@ -1332,11 +1370,11 @@ PART_MAPPING["text"] = function TextPartDisplay(props) {
     return items.filter((x) => !!x).join(" \u00B7 ")
   })

-  const displayText = () => (part().text ?? "").trim()
-  const throttledText = createThrottledValue(displayText)
   const streaming = createMemo(
     () => props.message.role === "assistant" && typeof (props.message as AssistantMessage).time.completed !== "number",
   )
+  const displayText = () => (part().text ?? "").trim()
+  const throttledText = createPacedValue(displayText, streaming)
   const isLastTextPart = createMemo(() => {
     const last = (data.store.part?.[props.message.id] ?? [])
       .filter((item): item is TextPart => item?.type === "text" && !!item.text?.trim())
@@ -1395,11 +1433,11 @@ PART_MAPPING["text"] = function TextPartDisplay(props) {

 PART_MAPPING["reasoning"] = function ReasoningPartDisplay(props) {
   const part = () => props.part as ReasoningPart
-  const text = () => part().text.trim()
-  const throttledText = createThrottledValue(text)
   const streaming = createMemo(
     () => props.message.role === "assistant" && typeof (props.message as AssistantMessage).time.completed !== "number",
   )
+  const text = () => part().text.trim()
+  const throttledText = createPacedValue(text, streaming)

   return (
     <Show when={throttledText()}>

PATCH

echo "Patch applied successfully."
