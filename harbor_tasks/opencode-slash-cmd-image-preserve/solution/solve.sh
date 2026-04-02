#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Check if already applied — look for the image-preserving pattern in handleSlashSelect
if grep -q '\.\.\.images' packages/app/src/components/prompt-input.tsx 2>/dev/null; then
  echo "Patch already applied"
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/app/src/components/prompt-input.tsx b/packages/app/src/components/prompt-input.tsx
index 1cc7c578d36..c8f72b8d2f5 100644
--- a/packages/app/src/components/prompt-input.tsx
+++ b/packages/app/src/components/prompt-input.tsx
@@ -624,17 +624,18 @@ export const PromptInput: Component<PromptInputProps> = (props) => {
     if (!cmd) return
     promptProbe.select(cmd.id)
     closePopover()
+    const images = imageAttachments()

     if (cmd.type === "custom") {
       const text = `/${cmd.trigger} `
       setEditorText(text)
-      prompt.set([{ type: "text", content: text, start: 0, end: text.length }], text.length)
+      prompt.set([{ type: "text", content: text, start: 0, end: text.length }, ...images], text.length)
       focusEditorEnd()
       return
     }

     clearEditor()
-    prompt.set([{ type: "text", content: "", start: 0, end: 0 }], 0)
+    prompt.set([...DEFAULT_PROMPT, ...images], 0)
     command.trigger(cmd.id, "slash")
   }

PATCH

echo "Patch applied successfully"
