#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for Keys.charAt() fix
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/Keys.java b/java/src/org/openqa/selenium/Keys.java
index de72b50107590..922178aab5f42 100644
--- a/java/src/org/openqa/selenium/Keys.java
+++ b/java/src/org/openqa/selenium/Keys.java
@@ -146,10 +146,10 @@ public int getCodePoint() {

   @Override
   public char charAt(int index) {
-    if (index == 0) {
-      return keyCode;
+    if (index != 0) {
+      throw new IndexOutOfBoundsException("Index: " + index + ", Length: 1");
     }
-    return 0;
+    return keyCode;
   }

   @Override
PATCH

echo "Patch applied successfully"
