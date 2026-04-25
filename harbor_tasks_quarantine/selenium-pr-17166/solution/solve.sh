#!/bin/bash
# Gold solution for selenium-keys-charsequence-contract task
set -e

cd /workspace/selenium

# Idempotency check - skip if already patched (check for specific error message in charAt)
if grep -q 'IndexOutOfBoundsException("Index: "' java/src/org/openqa/selenium/Keys.java; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/Keys.java b/java/src/org/openqa/selenium/Keys.java
index 1234567..abcdefg 100644
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

echo "Gold patch applied successfully"
