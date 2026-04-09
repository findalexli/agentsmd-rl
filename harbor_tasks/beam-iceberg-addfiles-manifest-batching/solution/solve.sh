#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'class CreateManifests' sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFiles.java 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix - <<'PATCH'
diff --git a/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFiles.java b/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFiles.java
index a19a257b49a5..4aca5e989771 100644
--- a/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFiles.java
+++ b/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFiles.java
@@ -21,7 +21,6 @@
 import static org.apache.beam.sdk.io.iceberg.AddFiles.ConvertToDataFile.ERRORS;
 import static org.apache.beam.sdk.metrics.Metrics.counter;
 import static org.apache.beam.sdk.util.Preconditions.checkStateNotNull;
-import static org.apache.beam.sdk.values.PCollection.IsBounded.BOUNDED;
 import static org.apache.beam.sdk.values.PCollection.IsBounded.UNBOUNDED;
 import static org.apache.beam.vendor.guava.v32_1_2_jre.com.google.common.base.Preconditions.checkState;
 
@@ -32,20 +31,21 @@
 import java.nio.charset.StandardCharsets;
 import java.util.ArrayList;
 import java.util.Collections;
-import java.util.HashMap;
 import java.util.Iterator;
 import java.util.LinkedList;
 import java.util.List;
 import java.util.Map;
 import java.util.Objects;
+import java.util.UUID;
 import java.util.concurrent.Callable;
 import java.util.concurrent.ExecutionException;
 import java.util.concurrent.ExecutorService;
 import java.util.concurrent.Executors;
 import java.util.concurrent.Future;
-import java.util.concurrent.Semaphore;
 import java.util.stream.Collectors;
 import java.util.stream.Stream;
+import org.apache.beam.sdk.coders.KvCoder;
+import org.apache.beam.sdk.coders.VarIntCoder;
 import org.apache.beam.sdk.coders.VarLongCoder;
 import org.apache.beam.sdk.io.Compression;
 import org.apache.beam.sdk.io.FileSystems;
@@ -59,13 +59,13 @@
 import org.apache.beam.sdk.state.StateSpecs;
 import org.apache.beam.sdk.state.ValueState;
 import org.apache.beam.sdk.transforms.DoFn;
-import org.apache.beam.sdk.transforms.GroupByKey;
 import org.apache.beam.sdk.transforms.GroupIntoBatches;
 import org.apache.beam.sdk.transforms.PTransform;
 import org.apache.beam.sdk.transforms.ParDo;
 import org.apache.beam.sdk.transforms.WithKeys;
 import org.apache.beam.sdk.transforms.windowing.BoundedWindow;
 import org.apache.beam.sdk.transforms.windowing.PaneInfo;
+import org.apache.beam.sdk.util.ShardedKey;
 import org.apache.beam.sdk.values.KV;
 import org.apache.beam.sdk.values.PCollection;
 import org.apache.beam.sdk.values.PCollectionRowTuple;
@@ -83,6 +83,10 @@
 import org.apache.iceberg.DataFile;
 import org.apache.iceberg.DataFiles;
 import org.apache.iceberg.FileFormat;
+import org.apache.iceberg.GenericManifestFile;
+import org.apache.iceberg.ManifestFile;
+import org.apache.iceberg.ManifestFiles;
+import org.apache.iceberg.ManifestWriter;
 import org.apache.iceberg.Metrics;
 import org.apache.iceberg.MetricsConfig;
 import org.apache.iceberg.PartitionField;
@@ -92,11 +96,10 @@
 import org.apache.iceberg.Table;
 import org.apache.iceberg.avro.Avro;
 import org.apache.iceberg.catalog.TableIdentifier;
-import org.apache.iceberg.data.Record;
 import org.apache.iceberg.exceptions.AlreadyExistsException;
 import org.apache.iceberg.exceptions.NoSuchTableException;
-import org.apache.iceberg.io.CloseableIterable;
 import org.apache.iceberg.io.InputFile;
+import org.apache.iceberg.io.OutputFile;
 import org.apache.iceberg.mapping.MappingUtil;
 import org.apache.iceberg.mapping.NameMapping;
 import org.apache.iceberg.orc.OrcMetrics;
@@ -105,8 +108,6 @@
 import org.apache.iceberg.transforms.Transform;
 import org.apache.iceberg.types.Conversions;
 import org.apache.iceberg.types.Type;
-import org.apache.iceberg.types.TypeUtil;
-import org.apache.iceberg.types.Types;
 import org.apache.parquet.hadoop.ParquetFileReader;
 import org.apache.parquet.hadoop.metadata.FileMetaData;
 import org.apache.parquet.hadoop.metadata.ParquetMetadata;
@@ -126,16 +127,20 @@ public class AddFiles extends PTransform<PCollection<String>, PCollectionRowTupl
   static final String OUTPUT_TAG = "snapshots";
   static final String ERROR_TAG = "errors";
   private static final Duration DEFAULT_TRIGGER_INTERVAL = Duration.standardMinutes(10);
-  private static final Counter numFilesAdded = counter(AddFiles.class, "numFilesAdded");
+  private static final Counter numManifestFilesAdded =
+      counter(AddFiles.class, "numManifestFilesAdded");
+  private static final Counter numDataFilesAdded = counter(AddFiles.class, "numDataFilesAdded");
   private static final Counter numErrorFiles = counter(AddFiles.class, "numErrorFiles");
   private static final Logger LOG = LoggerFactory.getLogger(AddFiles.class);
-  private static final int DEFAULT_FILES_TRIGGER = 10_000;
+  private static final int DEFAULT_DATAFILES_PER_MANIFEST = 10_000;
+  private static final int DEFAULT_MAX_MANIFESTS_PER_SNAPSHOT = 100;
   static final Schema ERROR_SCHEMA =
       Schema.builder().addStringField("file").addStringField("error").build();
+  private static final long MANIFEST_PREFIX = UUID.randomUUID().getMostSignificantBits();
   private final IcebergCatalogConfig catalogConfig;
   private final String tableIdentifier;
   private @Nullable Duration intervalTrigger;
-  private @Nullable Integer numFilesTrigger;
+  private final int manifestFileSize;
   private final @Nullable String locationPrefix;
   private final @Nullable List<String> partitionFields;
   private final @Nullable Map<String, String> tableProps;
@@ -146,14 +151,15 @@ public AddFiles(
       @Nullable String locationPrefix,
       @Nullable List<String> partitionFields,
       @Nullable Map<String, String> tableProps,
-      @Nullable Integer numFilesTrigger,
+      @Nullable Integer manifestFileSize,
       @Nullable Duration intervalTrigger) {
     this.catalogConfig = catalogConfig;
     this.tableIdentifier = tableIdentifier;
     this.partitionFields = partitionFields;
     this.tableProps = tableProps;
     this.intervalTrigger = intervalTrigger;
-    this.numFilesTrigger = numFilesTrigger;
+    this.manifestFileSize =
+        manifestFileSize != null ? manifestFileSize : DEFAULT_DATAFILES_PER_MANIFEST;
     this.locationPrefix = locationPrefix;
   }
 
@@ -161,15 +167,14 @@ public AddFiles(
   public PCollectionRowTuple expand(PCollection<String> input) {
     if (input.isBounded().equals(UNBOUNDED)) {
       intervalTrigger = intervalTrigger != null ? intervalTrigger : DEFAULT_TRIGGER_INTERVAL;
-      numFilesTrigger = numFilesTrigger != null ? numFilesTrigger : DEFAULT_FILES_TRIGGER;
       LOG.info(
-          "AddFiles configured to commit after accumulating {} files, or after {} seconds.",
-          numFilesTrigger,
+          "AddFiles configured to generate a new manifest after accumulating {} files, or after {} seconds.",
+          manifestFileSize,
           intervalTrigger.getStandardSeconds());
     } else {
       checkState(
-          intervalTrigger == null && numFilesTrigger == null,
-          "Specifying an interval trigger or file trigger is only supported for streaming pipelines.");
+          intervalTrigger == null,
+          "Specifying an interval trigger is only supported for streaming pipelines.");
     }
 
     if (!Strings.isNullOrEmpty(locationPrefix)) {
@@ -188,32 +193,44 @@ public PCollectionRowTuple expand(PCollection<String> input) {
                         partitionFields,
                         tableProps))
                 .withOutputTags(DATA_FILES, TupleTagList.of(ERRORS)));
-    SchemaCoder<SerializableDataFile> sdfSchema;
+    SchemaCoder<SerializableDataFile> sdfCoder;
     try {
-      sdfSchema = SchemaRegistry.createDefault().getSchemaCoder(SerializableDataFile.class);
+      sdfCoder = SchemaRegistry.createDefault().getSchemaCoder(SerializableDataFile.class);
     } catch (Exception e) {
       throw new RuntimeException(e);
     }
 
-    PCollection<KV<Void, SerializableDataFile>> keyedFiles =
+    PCollection<KV<Integer, SerializableDataFile>> keyedFiles =
         dataFiles
             .get(DATA_FILES)
-            .setCoder(sdfSchema)
-            .apply("AddStaticKey", WithKeys.of((Void) null));
+            .setCoder(sdfCoder)
+            .apply("AddSpecIdKey", WithKeys.of(SerializableDataFile::getPartitionSpecId))
+            .setCoder(KvCoder.of(VarIntCoder.of(), sdfCoder));
+
+    GroupIntoBatches<Integer, SerializableDataFile> batchDataFiles =
+        GroupIntoBatches.ofSize(manifestFileSize);
+    GroupIntoBatches<String, byte[]> batchManifestFiles =
+        GroupIntoBatches.ofSize(DEFAULT_MAX_MANIFESTS_PER_SNAPSHOT);
+
+    if (keyedFiles.isBounded().equals(UNBOUNDED)) {
+      batchDataFiles = batchDataFiles.withMaxBufferingDuration(checkStateNotNull(intervalTrigger));
+      batchManifestFiles =
+          batchManifestFiles.withMaxBufferingDuration(checkStateNotNull(intervalTrigger));
+    }
+
+    PCollection<KV<ShardedKey<Integer>, Iterable<SerializableDataFile>>> groupedFiles =
+        keyedFiles.apply("GroupDataFilesIntoBatches", batchDataFiles.withShardedKey());
 
-    PCollection<KV<Void, Iterable<SerializableDataFile>>> groupedFiles =
-        keyedFiles.isBounded().equals(BOUNDED)
-            ? keyedFiles.apply(GroupByKey.create())
-            : keyedFiles.apply(
-                GroupIntoBatches.<Void, SerializableDataFile>ofSize(
-                        checkStateNotNull(numFilesTrigger))
-                    .withMaxBufferingDuration(checkStateNotNull(intervalTrigger)));
+    PCollection<KV<String, byte[]>> manifests =
+        groupedFiles.apply(
+            "CreateManifests", ParDo.of(new CreateManifests(catalogConfig, tableIdentifier)));
 
     PCollection<Row> snapshots =
-        groupedFiles
+        manifests
+            .apply("GatherManifests", batchManifestFiles)
             .apply(
-                "CommitFilesToIceberg",
-                ParDo.of(new CommitFilesDoFn(catalogConfig, tableIdentifier)))
+                "CommitManifests",
+                ParDo.of(new CommitManifestFilesDoFn(catalogConfig, tableIdentifier)))
             .setRowSchema(SnapshotInfo.getSchema());
 
     return PCollectionRowTuple.of(
@@ -253,9 +270,6 @@ static class ConvertToDataFile extends DoFn<String, SerializableDataFile> {
     private transient @MonotonicNonNull LinkedList<Future<ProcessResult>> activeTasks;
     private transient volatile @MonotonicNonNull Table table;
 
-    // Limit open readers to avoid blowing up memory on one worker
-    private static final int MAX_READERS = 10;
-    private static final Semaphore ACTIVE_READERS = new Semaphore(MAX_READERS);
     // Number of parallel threads processing incoming files
     private static final int THREAD_POOL_SIZE = 10;
     private static final int MAX_IN_FLIGHT_TASKS = 100;
@@ -489,7 +503,6 @@ private Callable<ProcessResult> createProcessTask(
                 .withFileSizeInBytes(inputFile.getLength())
                 .withPartitionPath(partitionPath)
                 .build();
-
         return new ProcessResult(
             SerializableDataFile.from(df, partitionPath), null, timestamp, window, paneInfo);
       };
@@ -499,10 +512,6 @@ static <W, T> T transformValue(Transform<W, T> transform, Type type, ByteBuffer
       return transform.bind(type).apply(Conversions.fromByteBuffer(type, bytes));
     }
 
-    private static <W, T> T transformValue(Transform<W, T> transform, Type type, Object value) {
-      return transform.bind(type).apply((W) value);
-    }
-
     private Table getOrCreateTable(String filePath, FileFormat format) throws IOException {
       TableIdentifier tableId = TableIdentifier.parse(identifier);
       try {
@@ -555,11 +564,6 @@ private String getPartitionFromFilePath(String filePath) {
      * determine the partition. We also cannot fall back to a "null" partition, because that will
      * also get skipped by most queries.
      *
-     * <p>The Bucket partition transform is an exceptional case because it is not monotonic, meaning
-     * it's not enough to just compare the min and max values. There may be a middle value somewhere
-     * that gets hashed to a different value. For this transform, we'll need to read all the values
-     * in the column ensure they all get transformed to the same partition value.
-     *
      * <p>In these cases, we output the DataFile to the DLQ, because assigning an incorrect
      * partition may lead to it being incorrectly ignored by downstream queries.
      */
@@ -596,22 +600,9 @@ static String getPartitionFromMetrics(Metrics metrics, InputFile inputFile, Tabl
 
       PartitionKey pk = new PartitionKey(table.spec(), table.schema());
 
-      HashMap<Integer, PartitionField> bucketPartitions = new HashMap<>();
-      for (int i = 0; i < fields.size(); i++) {
-        PartitionField field = fields.get(i);
-        Transform<?, ?> transform = field.transform();
-        if (transform.toString().contains("bucket[")) {
-          bucketPartitions.put(i, field);
-        }
-      }
-
-      // first, read only metadata for the non-bucket partition types
+      // read metadata from footer and set partition based on min/max transformed values
       for (int i = 0; i < fields.size(); i++) {
         PartitionField field = fields.get(i);
-        // skip bucket partitions (we will process them below)
-        if (bucketPartitions.containsKey(i)) {
-          continue;
-        }
         Type type = table.schema().findType(field.sourceId());
         Transform<?, ?> transform = field.transform();
 
@@ -640,58 +631,65 @@ static String getPartitionFromMetrics(Metrics metrics, InputFile inputFile, Tabl
         pk.set(i, lowerTransformedValue);
       }
 
-      // bucket transform needs extra processing (see java doc above)
-      if (!bucketPartitions.isEmpty()) {
-        // Optimize by only reading bucket-transformed columns into memory
-        org.apache.iceberg.Schema bucketCols =
-            TypeUtil.select(
-                table.schema(),
-                bucketPartitions.values().stream()
-                    .map(PartitionField::sourceId)
-                    .collect(Collectors.toSet()));
-
-        // Keep one instance of transformed value per column. Use this to compare against each
-        // record's transformed value.
-        // Values in the same columns must yield the same transformed value, otherwise we cannot
-        // determine a partition
-        // from this file.
-        Map<Integer, Object> transformedValues = new HashMap<>();
-
-        // Do a one-time read of the file and compare all bucket-transformed columns
-        ACTIVE_READERS.acquire();
-        try (CloseableIterable<Record> reader = ReadUtils.createReader(inputFile, bucketCols)) {
-          for (Record record : reader) {
-            for (Map.Entry<Integer, PartitionField> entry : bucketPartitions.entrySet()) {
-              int partitionIndex = entry.getKey();
-              PartitionField partitionField = entry.getValue();
-              Transform<?, ?> transform = partitionField.transform();
-              Types.NestedField field = table.schema().findField(partitionField.sourceId());
-              Object value = record.getField(field.name());
-
-              // set initial transformed value for this column
-              @Nullable Object transformedValue = transformedValues.get(partitionIndex);
-              Object currentTransformedValue = transformValue(transform, field.type(), value);
-              if (transformedValue == null) {
-                transformedValues.put(partitionIndex, checkStateNotNull(currentTransformedValue));
-                continue;
-              }
+      return pk.toPath();
+    }
+  }
 
-              if (!Objects.deepEquals(currentTransformedValue, transformedValue)) {
-                throw new UnknownPartitionException(
-                    "Found records with conflicting transformed values, for column: "
-                        + field.name());
-              }
-            }
-          }
-        } finally {
-          ACTIVE_READERS.release();
-        }
+  /**
+   * Writes batches of {@link SerializableDataFile}s (grouped by Partition Spec ID) into {@link
+   * ManifestFile}s.
+   *
+   * <p>Returns the byte-encoded {@link ManifestFile}, to be reconstructed and committed by
+   * downstream {@link CommitManifestFilesDoFn}.
+   */
+  static class CreateManifests
+      extends DoFn<KV<ShardedKey<Integer>, Iterable<SerializableDataFile>>, KV<String, byte[]>> {
+    private final IcebergCatalogConfig catalogConfig;
+    private final String identifier;
+    private transient @MonotonicNonNull Table table;
+
+    public CreateManifests(IcebergCatalogConfig catalogConfig, String identifier) {
+      this.catalogConfig = catalogConfig;
+      this.identifier = identifier;
+    }
 
-        for (Map.Entry<Integer, Object> partitionCol : transformedValues.entrySet()) {
-          pk.set(partitionCol.getKey(), partitionCol.getValue());
+    @ProcessElement
+    public void process(
+        @Element KV<ShardedKey<Integer>, Iterable<SerializableDataFile>> batch,
+        OutputReceiver<KV<String, byte[]>> output)
+        throws IOException {
+      if (!batch.getValue().iterator().hasNext()) {
+        return;
+      }
+      if (table == null) {
+        table = catalogConfig.catalog().loadTable(TableIdentifier.parse(identifier));
+      }
+
+      PartitionSpec spec = checkStateNotNull(table.specs().get(batch.getKey().getKey()));
+
+      String manifestPath =
+          String.format(
+              "%s/metadata/%s-%s-m0.avro", table.location(), MANIFEST_PREFIX, UUID.randomUUID());
+      OutputFile outputFile = table.io().newOutputFile(manifestPath);
+
+      int numDataFiles = 0;
+      ManifestFile manifestFile;
+      try (ManifestWriter<DataFile> writer = ManifestFiles.write(spec, outputFile)) {
+        for (SerializableDataFile sdf : batch.getValue()) {
+          DataFile df = sdf.createDataFile(table.specs());
+          writer.add(df);
+          numDataFiles++;
         }
+        writer.close();
+        manifestFile = writer.toManifestFile();
+
+        // Provide a non-null dummy Snapshot ID to avoid encoding/decoding Null exceptions.
+        // The snapshot ID will be overwritten when the file is committed.
+        ((GenericManifestFile) manifestFile).set(6, -1L);
       }
-      return pk.toPath();
+
+      output.output(KV.of(identifier, ManifestFiles.encode(manifestFile)));
+      numDataFilesAdded.inc(numDataFiles);
     }
   }
 
@@ -707,13 +705,13 @@ static String getPartitionFromMetrics(Metrics metrics, InputFile inputFile, Tabl
    *   <li><b>Idempotency:</b> Prevents duplicate commits during bundle failures by calculating a
    *       deterministic hash for the file set. This ID is stored in the Iceberg {@code Snapshot}
    *       summary, under the key {@code "beam.add-files-commit-id"}. Before committing, the DoFn
-   *       travereses backwards through recent snapshots to check if the current batch's ID is
+   *       traverses backwards through recent snapshots to check if the current batch's ID is
    *       already present.
    * </ul>
    *
    * <p>Outputs the resulting Iceberg {@link Snapshot} information.
    */
-  static class CommitFilesDoFn extends DoFn<KV<Void, Iterable<SerializableDataFile>>, Row> {
+  static class CommitManifestFilesDoFn extends DoFn<KV<String, Iterable<byte[]>>, Row> {
     private final IcebergCatalogConfig catalogConfig;
     private final String identifier;
     private transient @MonotonicNonNull Table table = null;
@@ -723,17 +721,22 @@ static class CommitFilesDoFn extends DoFn<KV<Void, Iterable<SerializableDataFile
     private final StateSpec<ValueState<Long>> lastCommitTimestamp =
         StateSpecs.value(VarLongCoder.of());
 
-    public CommitFilesDoFn(IcebergCatalogConfig catalogConfig, String identifier) {
+    public CommitManifestFilesDoFn(IcebergCatalogConfig catalogConfig, String identifier) {
       this.catalogConfig = catalogConfig;
       this.identifier = identifier;
     }
 
     @ProcessElement
     public void process(
-        @Element KV<Void, Iterable<SerializableDataFile>> files,
+        @Element KV<String, Iterable<byte[]>> batch,
         @AlwaysFetched @StateId("lastCommitTimestamp") ValueState<Long> lastCommitTimestamp,
-        OutputReceiver<Row> output) {
-      String commitId = commitHash(files.getValue());
+        OutputReceiver<Row> output)
+        throws IOException {
+      List<ManifestFile> manifests = new ArrayList<>();
+      for (byte[] bytes : batch.getValue()) {
+        manifests.add(ManifestFiles.decode(bytes));
+      }
+      String commitId = commitHash(manifests);
       if (table == null) {
         table = catalogConfig.catalog().loadTable(TableIdentifier.parse(identifier));
       }
@@ -743,30 +746,29 @@ public void process(
         return;
       }
 
-      int numFiles = 0;
+      int numManifests = 0;
       AppendFiles appendFiles = table.newFastAppend();
-      for (SerializableDataFile file : files.getValue()) {
-        DataFile df = file.createDataFile(table.specs());
-        appendFiles.appendFile(df);
-        numFiles++;
+      for (ManifestFile file : manifests) {
+        appendFiles.appendManifest(file);
+        numManifests++;
       }
       appendFiles.set(COMMIT_ID_KEY, commitId);
-      LOG.info("Committing {} files, with commit ID: {}", numFiles, commitId);
+      LOG.info("Committing {} files, with commit ID: {}", numManifests, commitId);
       appendFiles.commit();
 
       Snapshot snapshot = table.currentSnapshot();
       output.output(SnapshotInfo.fromSnapshot(snapshot).toRow());
       lastCommitTimestamp.write(snapshot.timestampMillis());
-      numFilesAdded.inc(numFiles);
+      numManifestFilesAdded.inc(numManifests);
     }
 
-    private String commitHash(Iterable<SerializableDataFile> files) {
+    private String commitHash(Iterable<ManifestFile> files) {
       Hasher hasher = Hashing.sha256().newHasher();
 
       // Extract, sort, and hash to ensure deterministic output
       List<String> paths = new ArrayList<>();
-      for (SerializableDataFile file : files) {
-        paths.add(file.getPath());
+      for (ManifestFile file : files) {
+        paths.add(file.path());
       }
       Collections.sort(paths);
 
diff --git a/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFilesSchemaTransformProvider.java b/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFilesSchemaTransformProvider.java
index a04853c8ad96..87a63cdb7d46 100644
--- a/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFilesSchemaTransformProvider.java
+++ b/sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFilesSchemaTransformProvider.java
@@ -71,14 +71,11 @@ public static Builder builder() {
     public abstract @Nullable Map<String, String> getConfigProperties();
 
     @SchemaFieldDescription(
-        "For a streaming pipeline, sets the frequency at which incoming files are appended. Defaults to 600 (10 minutes). "
-            + "A commit is triggered when either this or append batch size is reached.")
+        "For a streaming pipeline, sets the frequency at which incoming files are appended (default 600, or 10min).")
     public abstract @Nullable Integer getTriggeringFrequencySeconds();
 
-    @SchemaFieldDescription(
-        "For a streaming pipeline, sets the desired number of appended files per commit. Defaults to 100,000 files. "
-            + "A commit is triggered when either this or append triggering interval is reached.")
-    public abstract @Nullable Integer getAppendBatchSize();
+    @SchemaFieldDescription("The number of data files per manifest (default 10,000 files).")
+    public abstract @Nullable Integer getManifestFileSize();
 
     @SchemaFieldDescription(
         "The prefix shared among all partitions. For example, a data file may have the following"
@@ -122,7 +119,7 @@ public abstract static class Builder {
 
       public abstract Builder setTriggeringFrequencySeconds(Integer triggeringFrequencySeconds);
 
-      public abstract Builder setAppendBatchSize(Integer size);
+      public abstract Builder setManifestFileSize(Integer size);
 
       public abstract Builder setLocationPrefix(String prefix);
 
@@ -176,7 +173,7 @@ public PCollectionRowTuple expand(PCollectionRowTuple input) {
                       configuration.getLocationPrefix(),
                       configuration.getPartitionFields(),
                       configuration.getTableProperties(),
-                      configuration.getAppendBatchSize(),
+                      configuration.getManifestFileSize(),
                       frequency != null ? Duration.standardSeconds(frequency) : null));
 
       PCollectionRowTuple output = PCollectionRowTuple.of("snapshots", result.get(OUTPUT_TAG));
diff --git a/sdks/java/io/iceberg/src/test/java/org/apache/beam/sdk/io/iceberg/AddFilesTest.java b/sdks/java/io/iceberg/src/test/java/org/apache/beam/sdk/io/iceberg/AddFilesTest.java
index 66a605c31dde..85740a33bd29 100644
--- a/sdks/java/io/iceberg/src/test/java/org/apache/beam/sdk/io/iceberg/AddFilesTest.java
+++ b/sdks/java/io/iceberg/src/test/java/org/apache/beam/sdk/io/iceberg/AddFilesTest.java
@@ -54,6 +54,7 @@
 import org.apache.iceberg.DataFile;
 import org.apache.iceberg.FileFormat;
 import org.apache.iceberg.Files;
+import org.apache.iceberg.ManifestFile;
 import org.apache.iceberg.Metrics;
 import org.apache.iceberg.MetricsConfig;
 import org.apache.iceberg.PartitionData;
@@ -79,6 +80,7 @@
 import org.joda.time.Duration;
 import org.junit.Before;
 import org.junit.ClassRule;
+import org.junit.Ignore;
 import org.junit.Rule;
 import org.junit.Test;
 import org.junit.rules.ExpectedException;
@@ -335,15 +337,15 @@ public void testStreamingAdds() throws IOException {
             TestStream.create(StringUtf8Coder.of())
                 .addElements(
                     paths.get(0),
-                    paths.subList(1, 15).toArray(new String[] {})) // should commit twice
+                    paths.subList(1, 15).toArray(new String[] {})) // should add one manifest file
                 .advanceProcessingTime(Duration.standardSeconds(10))
                 .addElements(
                     paths.get(15),
-                    paths.subList(16, 40).toArray(new String[] {})) // should commit 3 times
+                    paths.subList(16, 40).toArray(new String[] {})) // should add 3 manifest files
                 .advanceProcessingTime(Duration.standardSeconds(10))
                 .addElements(
                     paths.get(40),
-                    paths.subList(41, 45).toArray(new String[] {})) // should commit once
+                    paths.subList(41, 45).toArray(new String[] {})) // should add one manifest file
                 .advanceWatermarkToInfinity());
 
     files.apply(
@@ -361,14 +363,16 @@ public void testStreamingAdds() throws IOException {
 
     List<Snapshot> snapshots = Lists.newArrayList(table.snapshots());
     snapshots.sort(Comparator.comparingLong(Snapshot::timestampMillis));
-
-    assertEquals(6, snapshots.size());
-    assertEquals(10, Iterables.size(snapshots.get(0).addedDataFiles(table.io())));
-    assertEquals(5, Iterables.size(snapshots.get(1).addedDataFiles(table.io())));
-    assertEquals(10, Iterables.size(snapshots.get(2).addedDataFiles(table.io())));
-    assertEquals(10, Iterables.size(snapshots.get(3).addedDataFiles(table.io())));
-    assertEquals(5, Iterables.size(snapshots.get(4).addedDataFiles(table.io())));
-    assertEquals(5, Iterables.size(snapshots.get(5).addedDataFiles(table.io())));
+    List<ManifestFile> manifests = Iterables.getLast(snapshots).allManifests(table.io());
+    manifests.sort(Comparator.comparingLong(ManifestFile::sequenceNumber));
+
+    assertEquals(6, manifests.size());
+    assertEquals(10, (int) manifests.get(0).addedFilesCount());
+    assertEquals(5, (int) manifests.get(1).addedFilesCount());
+    assertEquals(10, (int) manifests.get(2).addedFilesCount());
+    assertEquals(10, (int) manifests.get(3).addedFilesCount());
+    assertEquals(5, (int) manifests.get(4).addedFilesCount());
+    assertEquals(5, (int) manifests.get(5).addedFilesCount());
   }
 
   @Test
@@ -422,6 +426,12 @@ public void testPartitionPrefixErrors() throws Exception {
     pipeline.run().waitUntilFinish();
   }
 
+  /**
+   * We reverted the in-depth bucket-partition validation in
+   * https://github.com/apache/beam/pull/38039, partly because it was too resource intensive, and
+   * also because the Spark AddFiles equivalent performs zero validation.
+   */
+  @Ignore
   @Test
   public void testRecognizesBucketPartitionMismatch() throws IOException {
     String file1 = root + "data1.parquet";

PATCH

echo "Patch applied successfully."
