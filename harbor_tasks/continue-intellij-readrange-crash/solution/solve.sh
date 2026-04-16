#!/bin/bash
set -e

cd /workspace/continue

git apply <<'PATCH'
diff --git a/extensions/intellij/src/main/kotlin/com/github/continuedev/continueintellijextension/continue/IntelliJIde.kt b/extensions/intellij/src/main/kotlin/com/github/continuedev/continueintellijextension/continue/IntelliJIde.kt
index ecb2dd009b2..29f93404ef5 100644
--- a/extensions/intellij/src/main/kotlin/com/github/continuedev/continueintellijextension/continue/IntelliJIde.kt
+++ b/extensions/intellij/src/main/kotlin/com/github/continuedev/continueintellijextension/continue/IntelliJIde.kt
@@ -352,13 +352,28 @@ class IntelliJIDE(
     override suspend fun readRangeInFile(filepath: String, range: Range): String {
         val fullContents = readFile(filepath)
         val lines = fullContents.lines()
-        val startLine = range.start.line
-        val startCharacter = range.start.character
-        val endLine = range.end.line
-        val endCharacter = range.end.character
+
+        // Safely clamp lines so we don't go out of bounds on the array
+        val startLine = range.start.line.coerceIn(0, maxOf(0, lines.size - 1))
+        val endLine = range.end.line.coerceIn(startLine, maxOf(0, lines.size - 1))
+
+        // Handle the single-line case properly so it doesn't mangle text
+        if (startLine == endLine) {
+            val line = lines.getOrNull(startLine) ?: return ""
+            val safeStart = range.start.character.coerceIn(0, line.length)
+            val safeEnd = range.end.character.coerceIn(safeStart, line.length)
+            return line.substring(safeStart, safeEnd)
+        }
+
+        // Clamp the character indexes to the actual string lengths to prevent the crash
+        val firstLineStr = lines.getOrNull(startLine) ?: ""
+        val safeStart = range.start.character.coerceIn(0, firstLineStr.length)
+        val firstLine = firstLineStr.substring(safeStart)
+
+        val lastLineStr = lines.getOrNull(endLine) ?: ""
+        val safeEnd = range.end.character.coerceIn(0, lastLineStr.length)
+        val lastLine = lastLineStr.substring(0, safeEnd)

-        val firstLine = lines.getOrNull(startLine)?.substring(startCharacter) ?: ""
-        val lastLine = lines.getOrNull(endLine)?.substring(0, endCharacter) ?: ""
         val betweenLines = if (endLine - startLine > 1) {
             lines.subList(startLine + 1, endLine).joinToString("\n")
         } else {
PATCH

# Idempotency check
grep -q "coerceIn" extensions/intellij/src/main/kotlin/com/github/continuedev/continueintellijextension/continue/IntelliJIde.kt