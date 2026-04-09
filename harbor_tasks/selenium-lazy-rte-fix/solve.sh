#!/bin/bash
set -e

cd /workspace/selenium

# Check if already applied (idempotency)
if git diff HEAD java/src/org/openqa/selenium/concurrent/Lazy.java | grep -q "catch (RuntimeException e)"; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
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
