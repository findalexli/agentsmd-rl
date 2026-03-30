#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

# Apply the gold patch from the PR diff
git apply --whitespace=fix - << 'PATCH'
diff --git a/extensions/telegram/src/format.ts b/extensions/telegram/src/format.ts
index 591e4c35a849..3fbe12243596 100644
--- a/extensions/telegram/src/format.ts
+++ b/extensions/telegram/src/format.ts
@@ -433,28 +433,21 @@ export function splitTelegramHtmlChunks(html: string, limit: number): string[] {
   return chunks.length > 0 ? chunks : [html];
 }

-function splitTelegramChunkByHtmlLimit(
-  chunk: MarkdownIR,
-  htmlLimit: number,
-  renderedHtmlLength: number,
-): MarkdownIR[] {
+function splitTelegramChunkByHtmlLimit(chunk: MarkdownIR, htmlLimit: number): MarkdownIR[] {
   const currentTextLength = chunk.text.length;
   if (currentTextLength <= 1) {
     return [chunk];
   }
-  const proportionalLimit = Math.floor(
-    (currentTextLength * htmlLimit) / Math.max(renderedHtmlLength, 1),
-  );
-  const candidateLimit = Math.min(currentTextLength - 1, proportionalLimit);
-  const splitLimit =
-    Number.isFinite(candidateLimit) && candidateLimit > 0
-      ? candidateLimit
-      : Math.max(1, Math.floor(currentTextLength / 2));
+  const splitLimit = findLargestTelegramChunkTextLengthWithinHtmlLimit(chunk, htmlLimit);
+  if (splitLimit <= 0) {
+    return [chunk];
+  }
   const split = splitMarkdownIRPreserveWhitespace(chunk, splitLimit);
-  if (split.length > 1) {
+  const firstChunk = split[0];
+  if (firstChunk && renderTelegramChunkHtml(firstChunk).length <= htmlLimit) {
     return split;
   }
-  return splitMarkdownIRPreserveWhitespace(chunk, Math.max(1, Math.floor(currentTextLength / 2)));
+  return [sliceMarkdownIR(chunk, 0, splitLimit), sliceMarkdownIR(chunk, splitLimit, currentTextLength)];
 }

 function sliceStyleSpans(
@@ -554,6 +547,26 @@ function renderTelegramChunkHtml(ir: MarkdownIR): string {
   return wrapFileReferencesInHtml(renderTelegramHtml(ir));
 }

+function findLargestTelegramChunkTextLengthWithinHtmlLimit(
+  chunk: MarkdownIR,
+  htmlLimit: number,
+): number {
+  const currentTextLength = chunk.text.length;
+  if (currentTextLength <= 1) {
+    return currentTextLength;
+  }
+
+  // Prefix HTML length is not monotonic because a sliced auto-link can render as
+  // a long <a ...> fragment, while a longer completed file ref de-linkifies to
+  // a shorter <code>...</code> wrapper. Search exact candidates instead.
+  for (let candidateLength = currentTextLength - 1; candidateLength >= 1; candidateLength -= 1) {
+    if (renderTelegramChunkHtml(sliceMarkdownIR(chunk, 0, candidateLength)).length <= htmlLimit) {
+      return candidateLength;
+    }
+  }
+  return 0;
+}
+
 function findMarkdownIRPreservedSplitIndex(text: string, start: number, limit: number): number {
   const maxEnd = Math.min(text.length, start + limit);
   if (maxEnd >= text.length) {
@@ -735,7 +748,7 @@ function renderTelegramChunksWithinHtmlLimit(
       finalized.push(chunk);
       continue;
     }
-    const split = splitTelegramChunkByHtmlLimit(chunk, normalizedLimit, html.length);
+    const split = splitTelegramChunkByHtmlLimit(chunk, normalizedLimit);
     if (split.length <= 1) {
       // Worst-case safety: avoid retry loops, deliver the chunk as-is.
       finalized.push(chunk);
PATCH
