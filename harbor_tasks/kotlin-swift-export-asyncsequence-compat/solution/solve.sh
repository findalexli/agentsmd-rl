#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency check)
if grep -q "public func asyncSequence<T>" native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat << 'PATCH' | git apply -
diff --git a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
index ad5e959952103..47d9675e44d6d 100644
--- a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
+++ b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
@@ -251,3 +251,12 @@ public final class KotlinFlowIterator<Element>: KotlinRuntime.KotlinBase, AsyncI
         }()
     }
 }
+
+/// This function provides source compatibility with KMP-NativeCoroutines during the migration to Swift Export.
+/// It should be replaced with a call to `asAsyncSequence()` once you have fully migrated to Swift Export.
+@available(*, deprecated, message: "Use `asAsyncSequence()` from Swift Export")
+public func asyncSequence<T>(
+    for flow: any KotlinTypedFlow<T>
+) -> KotlinFlowSequence<T> {
+    return flow.asAsyncSequence()
+}
PATCH

echo "Patch applied successfully"
