#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

if grep -q "replacementPreservesWordBoundary" src/utils/directive-tags.ts 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/src/utils/directive-tags.ts b/src/utils/directive-tags.ts
index 6d69e795b052..8dbbb2a05f5d 100644
--- a/src/utils/directive-tags.ts
+++ b/src/utils/directive-tags.ts
@@ -19,11 +19,21 @@ const REPLY_TAG_RE = /\[\[\s*(?:reply_to_current|reply_to\s*:\s*([^\]\n]+))\s*\]
 const INLINE_DIRECTIVE_TAG_WITH_PADDING_RE =
   /\s*(?:\[\[\s*audio_as_voice\s*\]\]|\[\[\s*(?:reply_to_current|reply_to\s*:\s*[^\]\n]+)\s*\]\])\s*/gi;
 
+function replacementPreservesWordBoundary(source: string, offset: number, length: number): string {
+  const before = source[offset - 1];
+  const after = source[offset + length];
+  return before && after && !/\s/u.test(before) && !/\s/u.test(after) ? " " : "";
+}
+
 function normalizeDirectiveWhitespace(text: string): string {
   return text
-    .replace(/[ \t]+/g, " ")
-    .replace(/[ \t]*\n[ \t]*/g, "\n")
-    .trim();
+    .replace(/\r\n/g, "\n")
+    .replace(/([^\s])[ \t]{2,}([^\s])/g, "$1 $2")
+    .replace(/^\n+/, "")
+    .replace(/^[ \t](?=\S)/, "")
+    .replace(/[ \t]+\n/g, "\n")
+    .replace(/\n{3,}/g, "\n\n")
+    .trimEnd();
 }
 
 type StripInlineDirectiveTagsResult = {
@@ -127,13 +137,13 @@ export function parseInlineDirectives(
   let sawCurrent = false;
   let lastExplicitId: string | undefined;
 
-  cleaned = cleaned.replace(AUDIO_TAG_RE, (match) => {
+  cleaned = cleaned.replace(AUDIO_TAG_RE, (match, offset, source) => {
     audioAsVoice = true;
     hasAudioTag = true;
-    return stripAudioTag ? " " : match;
+    return stripAudioTag ? replacementPreservesWordBoundary(source, offset, match.length) : match;
   });
 
-  cleaned = cleaned.replace(REPLY_TAG_RE, (match, idRaw: string | undefined) => {
+  cleaned = cleaned.replace(REPLY_TAG_RE, (match, idRaw: string | undefined, offset, source) => {
     hasReplyTag = true;
     if (idRaw === undefined) {
       sawCurrent = true;
@@ -143,7 +153,7 @@ export function parseInlineDirectives(
         lastExplicitId = id;
       }
     }
-    return stripReplyTags ? " " : match;
+    return stripReplyTags ? replacementPreservesWordBoundary(source, offset, match.length) : match;
   });
 
   cleaned = normalizeDirectiveWhitespace(cleaned);
PATCH
