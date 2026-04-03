#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'environment_type: options.environmentType' internal-packages/run-engine/src/batch-queue/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.cursor/rules/otel-metrics.mdc b/.cursor/rules/otel-metrics.mdc
new file mode 100644
index 00000000000..8efed4a7d51
--- /dev/null
+++ b/.cursor/rules/otel-metrics.mdc
@@ -0,0 +1,53 @@
+---
+description: Guidelines for creating OpenTelemetry metrics to avoid cardinality issues
+globs:
+  - "**/*.ts"
+---
+
+# OpenTelemetry Metrics Guidelines
+
+When creating or editing OTEL metrics (counters, histograms, gauges), always ensure metric attributes have **low cardinality**.
+
+## What is Cardinality?
+
+Cardinality refers to the number of unique values an attribute can have. Each unique combination of attribute values creates a new time series, which consumes memory and storage in your metrics backend.
+
+## Rules
+
+### DO use low-cardinality attributes:
+- **Enums**: `environment_type` (PRODUCTION, STAGING, DEVELOPMENT, PREVIEW)
+- **Booleans**: `hasFailures`, `streaming`, `success`
+- **Bounded error codes**: A finite, controlled set of error types
+- **Shard IDs**: When sharding is bounded (e.g., 0-15)
+
+### DO NOT use high-cardinality attributes:
+- **UUIDs/IDs**: `envId`, `userId`, `runId`, `projectId`, `organizationId`
+- **Unbounded integers**: `itemCount`, `batchSize`, `retryCount`
+- **Timestamps**: `createdAt`, `startTime`
+- **Free-form strings**: `errorMessage`, `taskName`, `queueName`
+
+## Example
+
+```typescript
+// BAD - High cardinality
+this.counter.add(1, {
+  envId: options.environmentId,        // UUID - unbounded
+  itemCount: options.runCount,         // Integer - unbounded
+});
+
+// GOOD - Low cardinality
+this.counter.add(1, {
+  environment_type: options.environmentType,  // Enum - 4 values
+  streaming: true,                            // Boolean - 2 values
+});
+```
+
+## Reference
+
+See the schedule engine (`internal-packages/schedule-engine/src/engine/index.ts`) for a good example of low-cardinality metric attributes.
+
+High cardinality metrics can cause:
+- Memory bloat in metrics backends (Axiom, Prometheus, etc.)
+- Slow queries and dashboard timeouts
+- Increased costs (many backends charge per time series)
+- Potential data loss or crashes at scale
diff --git a/internal-packages/run-engine/src/batch-queue/index.ts b/internal-packages/run-engine/src/batch-queue/index.ts
index 4ee337f7b40..c066df91504 100644
--- a/internal-packages/run-engine/src/batch-queue/index.ts
+++ b/internal-packages/run-engine/src/batch-queue/index.ts
@@ -287,8 +287,7 @@ export class BatchQueue {

     // Record metric
     this.batchesEnqueuedCounter?.add(1, {
-      envId: options.environmentId,
-      itemCount: options.runCount,
+      environment_type: options.environmentType,
       streaming: true,
     });

@@ -358,7 +357,7 @@ export class BatchQueue {
     });

     // Record metric
-    this.itemsEnqueuedCounter?.add(1, { envId });
+    this.itemsEnqueuedCounter?.add(1, { environment_type: meta.environmentType });

     this.logger.debug("Batch item enqueued", {
       batchId,
@@ -701,9 +700,8 @@ export class BatchQueue {
         "batch.attempt": storedMessage.attempt,
       });

-      // Record queue time metric (time from enqueue to processing)
+      // Calculate queue time (time from enqueue to processing)
       const queueTimeMs = Date.now() - storedMessage.timestamp;
-      this.itemQueueTimeHistogram?.record(queueTimeMs, { envId: storedMessage.tenantId });
       span?.setAttribute("batch.queueTimeMs", queueTimeMs);

       this.logger.debug("Processing batch item", {
@@ -734,6 +732,9 @@ export class BatchQueue {
         return;
       }

+      // Record queue time metric (requires meta for environment_type)
+      this.itemQueueTimeHistogram?.record(queueTimeMs, { environment_type: meta.environmentType });
+
       span?.setAttributes({
         "batch.runCount": meta.runCount,
         "batch.environmentId": meta.environmentId,
@@ -769,7 +770,7 @@ export class BatchQueue {
             return this.completionTracker.recordSuccess(batchId, result.runId, itemIndex);
           });

-          this.itemsProcessedCounter?.add(1, { envId: meta.environmentId });
+          this.itemsProcessedCounter?.add(1, { environment_type: meta.environmentType });
           this.logger.debug("Batch item processed successfully", {
             batchId,
             itemIndex,
@@ -808,7 +809,7 @@ export class BatchQueue {
           });

           this.itemsFailedCounter?.add(1, {
-            envId: meta.environmentId,
+            environment_type: meta.environmentType,
             errorCode: result.errorCode,
           });

@@ -848,7 +849,7 @@ export class BatchQueue {
         });

         this.itemsFailedCounter?.add(1, {
-          envId: meta.environmentId,
+          environment_type: meta.environmentType,
           errorCode: "UNEXPECTED_ERROR",
         });
         this.logger.error("Unexpected error processing batch item", {
@@ -914,14 +915,13 @@ export class BatchQueue {

       // Record metrics
       this.batchCompletedCounter?.add(1, {
-        envId: meta.environmentId,
+        environment_type: meta.environmentType,
         hasFailures: result.failedRunCount > 0,
       });

       const processingDuration = Date.now() - meta.createdAt;
       this.batchProcessingDurationHistogram?.record(processingDuration, {
-        envId: meta.environmentId,
-        itemCount: meta.runCount,
+        environment_type: meta.environmentType,
       });

       span?.setAttribute("batch.processingDurationMs", processingDuration);

PATCH

echo "Patch applied successfully."
