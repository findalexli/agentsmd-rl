# Improve Iceberg AddFiles Performance for Large File Batches

## Problem

The Iceberg `AddFiles` transform has performance bottlenecks when processing large numbers of files:

1. **Slow commits**: Each `DataFile` is added individually to Iceberg snapshots via `appendFile()`, which becomes very slow with thousands of files.

2. **Excessive memory from bucket partition validation**: The `getPartitionFromMetrics` method has special-case handling for bucket partitions that reads entire file contents into memory via `CloseableIterable<Record>` to validate that all records map to the same partition. This is gated by a `Semaphore` with only 10 permits, but still causes high memory usage. Notably, Spark's equivalent AddFiles operation performs no such validation.

3. **No parallelism in batching**: All files are grouped with a static `Void` key (`WithKeys.of((Void) null)`), forcing all file processing through a single worker.

## Expected Behavior

- Large file batches should be committed efficiently using Iceberg's bulk loading capabilities instead of individual file appends
- The bucket partition validation should be removed entirely (matching Spark's behavior)
- Files should be distributed across workers based on their partition spec for parallel processing

## Files to Look At

- `sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFiles.java` — Pipeline expansion, file batching, partition handling, and commit logic
- `sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/AddFilesSchemaTransformProvider.java` — Schema transform configuration
