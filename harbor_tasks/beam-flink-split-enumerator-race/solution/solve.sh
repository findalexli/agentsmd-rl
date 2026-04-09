#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'initializationLatch' runners/flink/src/main/java/org/apache/beam/runners/flink/translation/wrappers/streaming/io/source/LazyFlinkSourceSplitEnumerator.java 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/runners/flink/src/main/java/org/apache/beam/runners/flink/translation/wrappers/streaming/io/source/LazyFlinkSourceSplitEnumerator.java b/runners/flink/src/main/java/org/apache/beam/runners/flink/translation/wrappers/streaming/io/source/LazyFlinkSourceSplitEnumerator.java
index f5cd53c42ffa..94c14b2999b9 100644
--- a/runners/flink/src/main/java/org/apache/beam/runners/flink/translation/wrappers/streaming/io/source/LazyFlinkSourceSplitEnumerator.java
+++ b/runners/flink/src/main/java/org/apache/beam/runners/flink/translation/wrappers/streaming/io/source/LazyFlinkSourceSplitEnumerator.java
@@ -22,6 +22,7 @@
 import java.util.HashMap;
 import java.util.List;
 import java.util.Map;
+import java.util.concurrent.CountDownLatch;
 import javax.annotation.Nullable;
 import org.apache.beam.runners.flink.FlinkPipelineOptions;
 import org.apache.beam.sdk.io.BoundedSource;
@@ -53,7 +54,8 @@ public class LazyFlinkSourceSplitEnumerator<T>
   private final PipelineOptions pipelineOptions;
   private final int numSplits;
   private final List<FlinkSourceSplit<T>> pendingSplits;
-  private boolean splitsInitialized;
+  private volatile boolean splitsInitialized;
+  private final CountDownLatch initializationLatch = new CountDownLatch(1);

   public LazyFlinkSourceSplitEnumerator(
       SplitEnumeratorContext<FlinkSourceSplit<T>> context,
@@ -90,6 +92,8 @@ public void initializeSplits() {
             return pendingSplits;
           } catch (Exception e) {
             throw new RuntimeException(e);
+          } finally {
+            initializationLatch.countDown();
           }
         },
         (sourceSplits, error) -> {
@@ -97,6 +101,7 @@ public void initializeSplits() {
             pendingSplits.addAll(sourceSplits);
             throw new RuntimeException("Failed to start source enumerator.", error);
           }
+          splitsInitialized = true;
         });
   }

@@ -113,6 +118,16 @@ public void handleSplitRequest(int subtask, @Nullable String hostname) {
       LOG.info("Subtask {} {} is requesting a file source split", subtask, hostInfo);
     }

+    if (!splitsInitialized) {
+      try {
+        initializationLatch.await();
+      } catch (InterruptedException e) {
+        Thread.currentThread().interrupt();
+        LOG.warn("Interrupted while waiting for splits initialization", e);
+        return;
+      }
+    }
+
     if (!pendingSplits.isEmpty()) {
       final FlinkSourceSplit<T> split = pendingSplits.remove(pendingSplits.size() - 1);
       context.assignSplit(split, subtask);

PATCH

echo "Patch applied successfully."
