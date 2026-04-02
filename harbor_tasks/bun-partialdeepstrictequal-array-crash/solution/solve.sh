#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'SafeMapPrototypeSet' src/js/node/assert.ts; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/js/node/assert.ts b/src/js/node/assert.ts
index 3a19cd7c07c..7254dbde4f5 100644
--- a/src/js/node/assert.ts
+++ b/src/js/node/assert.ts
@@ -380,6 +380,8 @@ const SafeSetPrototypeIterator = SafeSet.prototype[SymbolIterator];
 const SafeMapPrototypeIterator = SafeMap.prototype[SymbolIterator];
 const SafeMapPrototypeHas = SafeMap.prototype.has;
 const SafeMapPrototypeGet = SafeMap.prototype.get;
+const SafeMapPrototypeSet = SafeMap.prototype.set;
+const SafeMapPrototypeDelete = SafeMap.prototype.delete;

 /**
  * Compares two objects or values recursively to check if they are equal.
@@ -471,13 +473,13 @@ function compareBranch(actual, expected, comparedObjects?) {
       let found = false;
       for (const { 0: key, 1: count } of expectedCounts) {
         if (isDeepStrictEqual(key, expectedItem)) {
-          expectedCounts.$set(key, count + 1);
+          SafeMapPrototypeSet.$call(expectedCounts, key, count + 1);
           found = true;
           break;
         }
       }
       if (!found) {
-        expectedCounts.$set(expectedItem, 1);
+        SafeMapPrototypeSet.$call(expectedCounts, expectedItem, 1);
       }
     }

@@ -486,9 +488,9 @@ function compareBranch(actual, expected, comparedObjects?) {
       for (const { 0: key, 1: count } of expectedCounts) {
         if (isDeepStrictEqual(key, actualItem)) {
           if (count === 1) {
-            expectedCounts.$delete(key);
+            SafeMapPrototypeDelete.$call(expectedCounts, key);
           } else {
-            expectedCounts.$set(key, count - 1);
+            SafeMapPrototypeSet.$call(expectedCounts, key, count - 1);
           }
           break;
         }

PATCH

echo "Fix applied successfully."
