#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'private transient DateTime startTime' sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/KafkaSourceConsumerFn.java 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/sdks/java/io/debezium/src/README.md b/sdks/java/io/debezium/src/README.md
index e56ac370b705..535213218856 100644
--- a/sdks/java/io/debezium/src/README.md
+++ b/sdks/java/io/debezium/src/README.md
@@ -155,12 +155,7 @@ There are two ways of initializing KSC:
 *  Restricted by number of records
 *  Restricted by amount of time (minutes)
 
-By default, DebeziumIO initializes it with the former, though user may choose the latter by setting the amount of minutes as a parameter:
-
-|Function|Param|Description|
-|-|-|-|
-|`KafkaSourceConsumerFn(connectorClass, recordMapper, maxRecords)`|_Class, SourceRecordMapper, Int_|Restrict run by number of records (Default).|
-|`KafkaSourceConsumerFn(connectorClass, recordMapper, timeToRun)`|_Class, SourceRecordMapper, Long_|Restrict run by amount of time (in minutes).|
+By default, DebeziumIO initializes it with the former, though user may choose the latter by setting the amount of minutes as a parameter for DebeziumIO.Read transform.
 
 ### Requirements and Supported versions
 
diff --git a/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/DebeziumIO.java b/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/DebeziumIO.java
index b38c035adf2d..ebf91a4a0957 100644
--- a/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/DebeziumIO.java
+++ b/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/DebeziumIO.java
@@ -63,11 +63,6 @@
  *
  * <h3>Usage example</h3>
  *
- * <p>Support is currently experimental. One of the known issues is that the connector does not
- * preserve the offset on a worker crash or restart, causing it to retrieve all the data from the
- * beginning again. See <a href="https://github.com/apache/beam/issues/28248">Issue #28248</a> for
- * details.
- *
  * <p>Connect to a Debezium - MySQL database and run a Pipeline
  *
  * <pre>
@@ -147,6 +142,8 @@ public abstract static class Read<T> extends PTransform<PBegin, PCollection<T>>
 
     abstract @Nullable Long getMaxTimeToRun();
 
+    abstract @Nullable Long getPollingTimeout();
+
     abstract @Nullable Coder<T> getCoder();
 
     abstract Builder<T> toBuilder();
@@ -163,6 +160,8 @@ abstract static class Builder<T> {
 
       abstract Builder<T> setMaxTimeToRun(Long miliseconds);
 
+      abstract Builder<T> setPollingTimeout(Long miliseconds);
+
       abstract Read<T> build();
     }
 
@@ -222,12 +221,18 @@ public Read<T> withMaxTimeToRun(Long miliseconds) {
       return toBuilder().setMaxTimeToRun(miliseconds).build();
     }
 
+    /**
+     * Sets the timeout in milliseconds for consumer polling request in the {@link
+     * KafkaSourceConsumerFn}. A lower timeout optimizes for latency. Increase the timeout if the
+     * consumer is not fetching any records. The default is 1000 milliseconds.
+     */
+    public Read<T> withPollingTimeout(Long miliseconds) {
+      return toBuilder().setPollingTimeout(miliseconds).build();
+    }
+
     protected Schema getRecordSchema() {
       KafkaSourceConsumerFn<T> fn =
-          new KafkaSourceConsumerFn<>(
-              getConnectorConfiguration().getConnectorClass().get(),
-              getFormatFunction(),
-              getMaxNumberOfRecords());
+          new KafkaSourceConsumerFn<>(getConnectorConfiguration().getConnectorClass().get(), this);
       fn.register(
           new KafkaSourceConsumerFn.OffsetTracker(
               new KafkaSourceConsumerFn.OffsetHolder(null, null, 0)));
@@ -267,10 +272,7 @@ public PCollection<T> expand(PBegin input) {
           .apply(
               ParDo.of(
                   new KafkaSourceConsumerFn<>(
-                      getConnectorConfiguration().getConnectorClass().get(),
-                      getFormatFunction(),
-                      getMaxNumberOfRecords(),
-                      getMaxTimeToRun())))
+                      getConnectorConfiguration().getConnectorClass().get(), this)))
           .setCoder(getCoder());
     }
   }
diff --git a/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/KafkaSourceConsumerFn.java b/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/KafkaSourceConsumerFn.java
index 00d7e6ac7411..fb4c2f21458f 100644
--- a/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/KafkaSourceConsumerFn.java
+++ b/sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/KafkaSourceConsumerFn.java
@@ -29,6 +29,7 @@
 import java.io.IOException;
 import java.io.Serializable;
 import java.lang.reflect.InvocationTargetException;
+import java.time.Duration;
 import java.util.ArrayList;
 import java.util.Arrays;
 import java.util.Collection;
@@ -48,6 +49,8 @@
 import org.apache.beam.sdk.transforms.splittabledofn.WatermarkEstimator;
 import org.apache.beam.sdk.transforms.splittabledofn.WatermarkEstimators;
 import org.apache.beam.sdk.transforms.windowing.BoundedWindow;
+import org.apache.beam.vendor.guava.v32_1_2_jre.com.google.common.base.MoreObjects;
+import org.apache.beam.vendor.guava.v32_1_2_jre.com.google.common.base.Stopwatch;
 import org.apache.beam.vendor.guava.v32_1_2_jre.com.google.common.collect.ImmutableMap;
 import org.apache.beam.vendor.guava.v32_1_2_jre.com.google.common.collect.Lists;
 import org.apache.beam.vendor.guava.v32_1_2_jre.com.google.common.collect.Streams;
@@ -60,7 +63,6 @@
 import org.apache.kafka.connect.storage.OffsetStorageReader;
 import org.checkerframework.checker.nullness.qual.Nullable;
 import org.joda.time.DateTime;
-import org.joda.time.Duration;
 import org.joda.time.Instant;
 import org.slf4j.Logger;
 import org.slf4j.LoggerFactory;
@@ -90,54 +92,37 @@
 public class KafkaSourceConsumerFn<T> extends DoFn<Map<String, String>, T> {
   private static final Logger LOG = LoggerFactory.getLogger(KafkaSourceConsumerFn.class);
   public static final String BEAM_INSTANCE_PROPERTY = "beam.parent.instance";
+  private static final Long DEFAULT_POLLING_TIMEOUT = 1000L;
 
   private final Class<? extends SourceConnector> connectorClass;
+  private final DebeziumIO.Read<T> spec;
   private final SourceRecordMapper<T> fn;
+  private final Long pollingTimeOut;
 
-  private final Long millisecondsToRun;
-  private final Integer maxRecords;
-
-  private static DateTime startTime;
+  private transient DateTime startTime;
   private static final Map<String, RestrictionTracker<OffsetHolder, Map<String, Object>>>
       restrictionTrackers = new ConcurrentHashMap<>();
 
-  /**
-   * Initializes the SDF with a time limit.
-   *
-   * @param connectorClass Supported Debezium connector class
-   * @param fn a SourceRecordMapper
-   * @param maxRecords Maximum number of records to fetch before finishing.
-   * @param millisecondsToRun Maximum time to run (in milliseconds)
-   */
-  @SuppressWarnings("unchecked")
-  KafkaSourceConsumerFn(
-      Class<?> connectorClass,
-      SourceRecordMapper<T> fn,
-      Integer maxRecords,
-      Long millisecondsToRun) {
-    this.connectorClass = (Class<? extends SourceConnector>) connectorClass;
-    this.fn = fn;
-    this.maxRecords = maxRecords;
-    this.millisecondsToRun = millisecondsToRun;
-  }
-
   /**
    * Initializes the SDF to be run indefinitely.
    *
    * @param connectorClass Supported Debezium connector class
-   * @param fn a SourceRecordMapper
-   * @param maxRecords Maximum number of records to fetch before finishing.
+   * @param spec a DebeziumIO.Read treansform
    */
-  KafkaSourceConsumerFn(Class<?> connectorClass, SourceRecordMapper<T> fn, Integer maxRecords) {
-    this(connectorClass, fn, maxRecords, null);
+  KafkaSourceConsumerFn(Class<?> connectorClass, DebeziumIO.Read<T> spec) {
+    // this(connectorClass, fn, maxRecords, null);
+    this.connectorClass = (Class<? extends SourceConnector>) connectorClass;
+    this.spec = spec;
+    this.fn = spec.getFormatFunction();
+    this.pollingTimeOut =
+        MoreObjects.firstNonNull(spec.getPollingTimeout(), DEFAULT_POLLING_TIMEOUT);
   }
 
   @SuppressFBWarnings("ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD")
   @GetInitialRestriction
   public OffsetHolder getInitialRestriction(@Element Map<String, String> unused)
       throws IOException {
-    KafkaSourceConsumerFn.startTime = new DateTime();
-    return new OffsetHolder(null, null, null, this.maxRecords, this.millisecondsToRun);
+    return new OffsetHolder(null, null, null, spec.getMaxNumberOfRecords(), spec.getMaxTimeToRun());
   }
 
   @NewTracker
@@ -211,6 +196,11 @@ private static Instant ensureTimestampWithinBounds(Instant timestamp) {
     return timestamp;
   }
 
+  @Setup
+  public void setup() {
+    startTime = DateTime.now();
+  }
+
   /**
    * Process the retrieved element and format it for output. Update all pending
    *
@@ -222,39 +212,61 @@ private static Instant ensureTimestampWithinBounds(Instant timestamp) {
    *     continue processing after 1 second. Otherwise, if we've reached a limit of elements, to
    *     stop processing.
    */
-  @DoFn.ProcessElement
+  @ProcessElement
   public ProcessContinuation process(
       @Element Map<String, String> element,
       RestrictionTracker<OffsetHolder, Map<String, Object>> tracker,
-      OutputReceiver<T> receiver)
-      throws Exception {
+      OutputReceiver<T> receiver) {
+
+    if (spec.getMaxNumberOfRecords() != null
+        && tracker.currentRestriction().fetchedRecords != null
+        && tracker.currentRestriction().fetchedRecords >= spec.getMaxNumberOfRecords()) {
+      return ProcessContinuation.stop();
+    }
+
     Map<String, String> configuration = new HashMap<>(element);
 
     // Adding the current restriction to the class object to be found by the database history
     register(tracker);
     configuration.put(BEAM_INSTANCE_PROPERTY, this.getHashCode());
 
-    SourceConnector connector = connectorClass.getDeclaredConstructor().newInstance();
-    connector.start(configuration);
-
-    SourceTask task = (SourceTask) connector.taskClass().getDeclaredConstructor().newInstance();
+    SourceConnector connector;
+    SourceTask task;
+    try {
+      connector = connectorClass.getDeclaredConstructor().newInstance();
+      connector.start(configuration);
+      task = (SourceTask) connector.taskClass().getDeclaredConstructor().newInstance();
+    } catch (InvocationTargetException
+        | InstantiationException
+        | IllegalAccessException
+        | NoSuchMethodException e) {
+      throw new RuntimeException(e);
+    }
 
+    Duration remainingTimeout = Duration.ofMillis(pollingTimeOut);
     try {
       Map<String, ?> consumerOffset = tracker.currentRestriction().offset;
       LOG.debug("--------- Consumer offset from Debezium Tracker: {}", consumerOffset);
 
-      task.initialize(new BeamSourceTaskContext(tracker.currentRestriction().offset));
+      task.initialize(new BeamSourceTaskContext(consumerOffset));
       task.start(connector.taskConfigs(1).get(0));
+      final Stopwatch pollTimer = Stopwatch.createUnstarted();
 
-      List<SourceRecord> records = task.poll();
+      while (Duration.ZERO.compareTo(remainingTimeout) < 0) {
+        pollTimer.reset().start();
+        List<SourceRecord> records = task.poll();
 
-      if (records == null) {
-        LOG.debug("-------- Pulled records null");
-        return ProcessContinuation.stop();
-      }
+        try {
+          remainingTimeout = remainingTimeout.minus(pollTimer.elapsed());
+        } catch (ArithmeticException e) {
+          remainingTimeout = Duration.ZERO;
+        }
+
+        if (records == null || records.isEmpty()) {
+          LOG.debug("-------- Pulled records null or empty");
+          break;
+        }
 
-      LOG.debug("-------- {} records found", records.size());
-      while (records != null && !records.isEmpty()) {
         for (SourceRecord record : records) {
           LOG.debug("-------- Record found: {}", record);
 
@@ -272,7 +284,6 @@ public ProcessContinuation process(
           receiver.outputWithTimestamp(json, recordInstant);
         }
         task.commit();
-        records = task.poll();
       }
     } catch (Exception ex) {
       throw new RuntimeException("Error occurred when consuming changes from Database. ", ex);
@@ -283,12 +294,14 @@ public ProcessContinuation process(
       task.stop();
     }
 
-    long elapsedTime = System.currentTimeMillis() - KafkaSourceConsumerFn.startTime.getMillis();
-    if (millisecondsToRun != null && millisecondsToRun > 0 && elapsedTime >= millisecondsToRun) {
-      return ProcessContinuation.stop();
-    } else {
-      return ProcessContinuation.resume().withResumeDelay(Duration.standardSeconds(1));
+    if (spec.getMaxTimeToRun() != null && spec.getMaxTimeToRun() > 0) {
+      long elapsedTime = System.currentTimeMillis() - startTime.getMillis();
+      if (elapsedTime >= spec.getMaxTimeToRun()) {
+        return ProcessContinuation.stop();
+      }
     }
+    return ProcessContinuation.resume()
+        .withResumeDelay(org.joda.time.Duration.millis(remainingTimeout.toMillis()));
   }
 
   public String getHashCode() {
@@ -418,17 +431,8 @@ static class OffsetTracker extends RestrictionTracker<OffsetHolder, Map<String,
     /**
      * Overriding {@link #tryClaim} in order to stop fetching records from the database.
      *
-     * <p>This works on two different ways:
-     *
-     * <h3>Number of records</h3>
-     *
-     * <p>This is the default behavior. Once the specified number of records has been reached, it
-     * will stop fetching them.
-     *
-     * <h3>Time based</h3>
-     *
-     * User may specify the amount of time the connector to be kept alive. Please see {@link
-     * KafkaSourceConsumerFn} for more details on this.
+     * <p>If number of record has been set, once the specified number of records has been reached,
+     * it will stop fetching them.
      *
      * @param position Currently not used
      * @return boolean
@@ -436,23 +440,20 @@ static class OffsetTracker extends RestrictionTracker<OffsetHolder, Map<String,
     @Override
     public boolean tryClaim(Map<String, Object> position) {
       LOG.debug("-------------- Claiming {} used to have: {}", position, restriction.offset);
-      long elapsedTime = System.currentTimeMillis() - startTime.getMillis();
       int fetchedRecords =
-          this.restriction.fetchedRecords == null ? 0 : this.restriction.fetchedRecords + 1;
+          this.restriction.fetchedRecords == null ? 0 : this.restriction.fetchedRecords;
       LOG.debug("------------Fetched records {} / {}", fetchedRecords, this.restriction.maxRecords);
-      LOG.debug(
-          "-------------- Time running: {} / {}", elapsedTime, (this.restriction.millisToRun));
       this.restriction.offset = position;
-      this.restriction.fetchedRecords = fetchedRecords;
       LOG.debug("-------------- History: {}", this.restriction.history);
 
-      // If we've reached the maximum number of records OR the maximum time, we reject
-      // the attempt to claim.
-      // If we've reached neither, then we continue approve the claim.
-      return (this.restriction.maxRecords == null || fetchedRecords < this.restriction.maxRecords)
-          && (this.restriction.millisToRun == null
-              || this.restriction.millisToRun == -1
-              || elapsedTime < this.restriction.millisToRun);
+      // If we've reached the maximum number of records, we reject the attempt to claim.
+      // Otherwise, we approve the claim.
+      boolean claimed =
+          (this.restriction.maxRecords == null || fetchedRecords < this.restriction.maxRecords);
+      if (claimed) {
+        this.restriction.fetchedRecords = fetchedRecords + 1;
+      }
+      return claimed;
     }
 
     @Override

PATCH

echo "Patch applied successfully."
