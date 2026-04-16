#!/bin/bash
set -euo pipefail

cd /workspace/selenium

# Idempotency check - skip if already patched
if grep -q 'catch (RuntimeException e)' java/src/org/openqa/selenium/concurrent/Lazy.java 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/concurrent/Lazy.java b/java/src/org/openqa/selenium/concurrent/Lazy.java
index 909988b480865..a057aa2ef55e7 100644
--- a/java/src/org/openqa/selenium/concurrent/Lazy.java
+++ b/java/src/org/openqa/selenium/concurrent/Lazy.java
@@ -42,6 +42,8 @@ public T get() {
         if (value == null) {
           try {
             value = supplier.get();
+          } catch (RuntimeException e) {
+            throw e;
           } catch (Exception e) {
             throw new InitializationException(e);
           }
PATCH

echo "Patch applied successfully"
