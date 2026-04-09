#!/bin/bash
set -e

cd /workspace/chroma

# Idempotency check: if already patched, exit
if grep -q "Unsupported operation for rebuild" rust/segment/src/types.rs; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/rust/segment/src/types.rs b/rust/segment/src/types.rs
index 9e4df381208..c1b5c4ecba6 100644
--- a/rust/segment/src/types.rs
+++ b/rust/segment/src/types.rs
@@ -111,6 +111,8 @@ pub enum LogMaterializerError {
     LogIndexOutOfBounds(usize),
     #[error("Record segment reader required but not available")]
     RecordSegmentReaderRequired,
+    #[error("Unsupported operation for rebuild: {0:?}")]
+    UnsupportedOperationForRebuild(Operation),
 }

 impl ChromaError for LogMaterializerError {
@@ -121,6 +123,7 @@ impl ChromaError for LogMaterializerError {
             LogMaterializerError::RecordSegment(e) => e.code(),
             LogMaterializerError::LogIndexOutOfBounds(_) => ErrorCodes::Internal,
             LogMaterializerError::RecordSegmentReaderRequired => ErrorCodes::Internal,
+            LogMaterializerError::UnsupportedOperationForRebuild(_) => ErrorCodes::Internal,
         }
     }
 }
@@ -972,6 +975,38 @@ pub async fn materialize_logs(
     })
 }

+pub async fn materialize_logs_for_rebuild(
+    logs: Chunk<LogRecord>,
+    offset_ids: Vec<u32>,
+) -> Result<MaterializeLogsResult, LogMaterializerError> {
+    TOTAL_LOGS_PRE_MATERIALIZED.add(logs.len() as u64, &[]);
+
+    let mut res = Vec::with_capacity(logs.len());
+
+    for ((log_record, log_index), offset_id) in logs.iter().zip(offset_ids.into_iter()) {
+        if log_record.record.operation != Operation::Add {
+            return Err(LogMaterializerError::UnsupportedOperationForRebuild(
+                log_record.record.operation,
+            ));
+        }
+
+        let mut materialized =
+            MaterializedLogRecord::from_log_record(offset_id, log_index, log_record)?;
+        materialized.offset_id_exists_in_segment = true;
+        materialized.final_operation = MaterializedLogOperation::AddNew;
+
+        res.push(materialized);
+    }
+
+    TOTAL_LOGS_POST_MATERIALIZED.add(res.len() as u64, &[]);
+
+    Ok(MaterializeLogsResult {
+        logs,
+        materialized: Chunk::new(res.into()),
+        has_backfill: false, // Rebuild path never has backfill
+    })
+}
+
 #[derive(Clone, Debug)]
 #[allow(clippy::large_enum_variant)]
 pub enum VectorSegmentWriter {
diff --git a/rust/worker/src/execution/operators/mod.rs b/rust/worker/src/execution/operators/mod.rs
index 819e68f426a..37cfadf208f 100644
--- a/rust/worker/src/execution/operators/mod.rs
+++ b/rust/worker/src/execution/operators/mod.rs
@@ -34,5 +34,6 @@ pub mod ranked_group_by;
 pub mod repair_log_offsets;
 pub mod select;
 pub mod source_record_segment;
+pub mod source_record_segment_v2;
 pub mod sparse_index_knn;
 pub mod sparse_log_knn;
diff --git a/rust/worker/src/execution/operators/source_record_segment.rs b/rust/worker/src/execution/operators/source_record_segment.rs
index feb603bd5c4..f2681c44577 100644
--- a/rust/worker/src/execution/operators/source_record_segment.rs
+++ b/rust/worker/src/execution/operators/source_record_segment.rs
@@ -19,6 +19,18 @@ use thiserror::Error;
 #[derive(Clone, Debug)]
 pub struct SourceRecordSegmentOperator {}

+impl SourceRecordSegmentOperator {
+    pub fn new() -> Self {
+        Self {}
+    }
+}
+
+impl Default for SourceRecordSegmentOperator {
+    fn default() -> Self {
+        Self::new()
+    }
+}
+
 #[derive(Clone, Debug)]
 pub struct SourceRecordSegmentInput {
     pub record_segment_reader: Option<RecordSegmentReader<'static>>,
@@ -66,7 +78,7 @@ impl Operator<SourceRecordSegmentInput, SourceRecordSegmentOutput> for SourceRec
                                     meta.into_iter().map(|(k, v)| (k, v.into())).collect()
                                 }),
                                 document: rec.document.map(ToString::to_string),
-                                operation: chroma_types::Operation::Upsert,
+                                operation: chroma_types::Operation::Add,
                             },
                         })
                     })
@@ -124,7 +136,7 @@ mod tests {
         for (offset, (record, _)) in source_output.iter().enumerate() {
             assert_eq!(record.log_offset, offset as i64 + 1);
             assert_eq!(record.record.id, int_as_id(offset + 1));
-            assert_eq!(record.record.operation, Operation::Upsert);
+            assert_eq!(record.record.operation, Operation::Add);
         }
     }
 }
diff --git a/rust/worker/src/execution/operators/source_record_segment_v2.rs b/rust/worker/src/execution/operators/source_record_segment_v2.rs
new file mode 100644
index 00000000000..a2b45e1cb46
--- /dev/null
+++ b/rust/worker/src/execution/operators/source_record_segment_v2.rs
@@ -0,0 +1,242 @@
+use crate::execution::operators::materialize_logs::MaterializeLogOutput;
+use async_trait::async_trait;
+use chroma_error::{ChromaError, ErrorCodes};
+use chroma_segment::blockfile_record::RecordSegmentReader;
+use chroma_system::Operator;
+use chroma_types::{Chunk, LogRecord, Operation, OperationRecord};
+use futures::StreamExt;
+use thiserror::Error;
+
+/// The `SourceRecordSegmentV2Operator` streams through the record segment and produces
+/// partitioned materialized log records for rebuild operations.
+/// This combines the functionality of SourceRecordSegment, Partition, and MaterializeLog operators.
+///
+/// # Parameters
+/// - `max_partition_size`: Maximum size of each partition
+///
+/// # Inputs
+/// - `record_reader`: The record segment reader, if the collection is initialized
+///
+/// # Outputs
+/// - Vec of MaterializeLogsResult (one per partition)
+///
+/// TODO(tanujnay112): This will replace SourceRecordSegmentOperator for full rebuilds once
+/// this code bakes.
+#[derive(Clone, Debug)]
+pub struct SourceRecordSegmentV2Operator {
+    max_partition_size: usize,
+}
+
+impl SourceRecordSegmentV2Operator {
+    pub fn new(max_partition_size: usize) -> Self {
+        Self { max_partition_size }
+    }
+}
+
+#[derive(Clone, Debug)]
+pub struct SourceRecordSegmentV2Input {
+    pub record_segment_reader: Option<RecordSegmentReader<'static>>,
+}
+
+#[derive(Debug, Clone)]
+pub struct SourceRecordSegmentV2Output {
+    pub partitions: Vec<MaterializeLogOutput>,
+    pub total_records: usize,
+}
+
+#[derive(Debug, Error)]
+pub enum SourceRecordSegmentV2Error {
+    #[error("Error reading record segment: {0}")]
+    RecordSegment(#[from] Box<dyn ChromaError>),
+    #[error("Error materializing logs: {0}")]
+    MaterializeLogs(#[from] chroma_segment::types::LogMaterializerError),
+}
+
+impl ChromaError for SourceRecordSegmentV2Error {
+    fn code(&self) -> ErrorCodes {
+        match self {
+            SourceRecordSegmentV2Error::RecordSegment(e) => e.code(),
+            SourceRecordSegmentV2Error::MaterializeLogs(e) => e.code(),
+        }
+    }
+}
+
+#[async_trait]
+impl Operator<SourceRecordSegmentV2Input, SourceRecordSegmentV2Output>
+    for SourceRecordSegmentV2Operator
+{
+    type Error = SourceRecordSegmentV2Error;
+
+    async fn run(
+        &self,
+        input: &SourceRecordSegmentV2Input,
+    ) -> Result<SourceRecordSegmentV2Output, SourceRecordSegmentV2Error> {
+        tracing::trace!("[{}]: {:?}", self.get_name(), input);
+
+        let reader = match input.record_segment_reader.as_ref() {
+            Some(reader) => reader,
+            None => {
+                return Ok(SourceRecordSegmentV2Output {
+                    partitions: vec![],
+                    total_records: 0,
+                });
+            }
+        };
+
+        let mut partitions = Vec::new();
+        let mut current_partition_logs = Vec::new();
+        let mut current_partition_offsets = Vec::new();
+        let mut total_records = 0;
+        let mut log_offset = 1;
+
+        let mut stream = reader.get_data_stream(..).await;
+
+        while let Some(result) = stream.next().await {
+            let (offset_id, record) = result?;
+            let log_record = LogRecord {
+                log_offset,
+                record: OperationRecord {
+                    id: record.id.to_string(),
+                    embedding: Some(record.embedding.to_vec()),
+                    encoding: Some(chroma_types::ScalarEncoding::FLOAT32),
+                    metadata: record
+                        .metadata
+                        .map(|meta| meta.into_iter().map(|(k, v)| (k, v.into())).collect()),
+                    document: record.document.map(ToString::to_string),
+                    operation: Operation::Add,
+                },
+            };
+            // Store offset ID in the same order as logs
+            current_partition_offsets.push(offset_id);
+            current_partition_logs.push(log_record);
+            total_records += 1;
+            log_offset += 1;
+
+            if current_partition_logs.len() >= self.max_partition_size {
+                let logs_chunk = Chunk::new(current_partition_logs.into());
+
+                let materialized = chroma_segment::types::materialize_logs_for_rebuild(
+                    logs_chunk,
+                    current_partition_offsets,
+                )
+                .await?;
+
+                let output = MaterializeLogOutput {
+                    result: materialized,
+                    collection_logical_size_delta: 0,
+                };
+
+                partitions.push(output);
+                current_partition_logs = Vec::new();
+                current_partition_offsets = Vec::new();
+            }
+        }
+
+        if !current_partition_logs.is_empty() {
+            let logs_chunk = Chunk::new(current_partition_logs.into());
+
+            let materialized = chroma_segment::types::materialize_logs_for_rebuild(
+                logs_chunk,
+                current_partition_offsets,
+            )
+            .await?;
+
+            let output = MaterializeLogOutput {
+                result: materialized,
+                collection_logical_size_delta: 0,
+            };
+
+            partitions.push(output);
+        }
+
+        Ok(SourceRecordSegmentV2Output {
+            partitions,
+            total_records,
+        })
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use chroma_log::test::{upsert_generator, LoadFromGenerator};
+    use chroma_segment::test::TestDistributedSegment;
+    use chroma_types::MaterializedLogOperation;
+
+    async fn setup_test_reader(num_records: usize) -> RecordSegmentReader<'static> {
+        let mut test_segment = TestDistributedSegment::new().await;
+        test_segment
+            .populate_with_generator(num_records, upsert_generator)
+            .await;
+        Box::pin(RecordSegmentReader::from_segment(
+            &test_segment.record_segment,
+            &test_segment.blockfile_provider,
+            None,
+        ))
+        .await
+        .expect("Record segment reader should be initialized")
+    }
+
+    #[tokio::test]
+    async fn test_source_v2_basic() {
+        let reader = setup_test_reader(100).await;
+        let input = SourceRecordSegmentV2Input {
+            record_segment_reader: Some(reader),
+        };
+
+        let operator = SourceRecordSegmentV2Operator::new(30);
+        let output = operator.run(&input).await.expect("Operator should succeed");
+
+        assert_eq!(output.total_records, 100);
+        assert_eq!(output.partitions.len(), 4); // 30, 30, 30, 10
+
+        // Verify partition sizes
+        assert_eq!(output.partitions[0].result.len(), 30);
+        assert_eq!(output.partitions[1].result.len(), 30);
+        assert_eq!(output.partitions[2].result.len(), 30);
+        assert_eq!(output.partitions[3].result.len(), 10);
+
+        // Verify operations are correct
+        for partition in &output.partitions {
+            for record in partition.result.iter() {
+                // For rebuild, we expect AddNew operation
+                assert_eq!(record.get_operation(), MaterializedLogOperation::AddNew);
+            }
+        }
+    }
+
+    #[tokio::test]
+    async fn test_source_v2_empty() {
+        let input = SourceRecordSegmentV2Input {
+            record_segment_reader: None,
+        };
+
+        let operator = SourceRecordSegmentV2Operator::new(30);
+        let output = operator.run(&input).await.expect("Operator should succeed");
+
+        assert_eq!(output.total_records, 0);
+        assert_eq!(output.partitions.len(), 0);
+    }
+
+    #[tokio::test]
+    async fn test_source_v2_preserves_offset_ids() {
+        let reader = setup_test_reader(10).await;
+        let input = SourceRecordSegmentV2Input {
+            record_segment_reader: Some(reader),
+        };
+
+        let operator = SourceRecordSegmentV2Operator::new(5);
+        let output = operator.run(&input).await.expect("Operator should succeed");
+
+        assert_eq!(output.partitions.len(), 2);
+
+        // Verify offset IDs are preserved (0-based from test data generation)
+        let mut expected_offset_id = 1u32;
+        for partition in &output.partitions {
+            for record in partition.result.iter() {
+                assert_eq!(record.get_offset_id(), expected_offset_id);
+                expected_offset_id += 1;
+            }
+        }
+    }
+}
diff --git a/rust/worker/src/execution/orchestration/compact.rs b/rust/worker/src/execution/orchestration/compact.rs
index bb6fd8154bb..38e5952b9b1 100644
--- a/rust/worker/src/execution/orchestration/compact.rs
+++ b/rust/worker/src/execution/orchestration/compact.rs
@@ -1148,6 +1148,282 @@ mod tests {
             .collect()
     }

+    #[tokio::test]
+    async fn test_metadata_rebuild_fts() {
+        let config = RootConfig::default();
+        let system = System::default();
+        let registry = Registry::new();
+        let dispatcher = Dispatcher::try_from_config(&config.query_service.dispatcher, &registry)
+            .await
+            .expect("Should be able to initialize dispatcher");
+        let dispatcher_handle = system.start_component(dispatcher);
+        let mut sysdb = SysDb::Test(TestSysDb::new());
+        let test_segments = TestDistributedSegment::new().await;
+        let collection_id = test_segments.collection.collection_id;
+        let database_name =
+            chroma_types::DatabaseName::new(test_segments.collection.database.clone())
+                .expect("database name should be valid");
+        sysdb
+            .create_collection(
+                test_segments.collection.tenant.clone(),
+                database_name.clone(),
+                collection_id,
+                test_segments.collection.name.clone(),
+                vec![
+                    test_segments.record_segment.clone(),
+                    test_segments.metadata_segment.clone(),
+                    test_segments.vector_segment.clone(),
+                ],
+                None,
+                None,
+                None,
+                test_segments.collection.dimension,
+                false,
+            )
+            .await
+            .expect("Collection create should be successful");
+
+        let mut in_memory_log = InMemoryLog::new();
+
+        // Add records with documents that we can search for
+        let records_with_docs = [
+            (1, "The quick brown fox jumps over the lazy dog"),
+            (2, "Machine learning algorithms are powerful tools"),
+            (3, "Full-text search enables efficient document retrieval"),
+            (4, "The brown dog chased the fox quickly"),
+            (5, "Search algorithms optimize for speed and accuracy"),
+        ];
+
+        for (idx, (id, doc)) in records_with_docs.iter().enumerate() {
+            let record = chroma_types::LogRecord {
+                log_offset: idx as i64,
+                record: chroma_types::OperationRecord {
+                    id: chroma_log::test::int_as_id(*id),
+                    embedding: Some(vec![0.0; TEST_EMBEDDING_DIMENSION]),
+                    encoding: Some(chroma_types::ScalarEncoding::FLOAT32),
+                    metadata: Some(HashMap::from([(
+                        "key".to_string(),
+                        chroma_types::UpdateMetadataValue::Str(format!("value_{}", id)),
+                    )])),
+                    document: Some(doc.to_string()),
+                    operation: chroma_types::Operation::Add,
+                },
+            };
+            in_memory_log.add_log(
+                collection_id,
+                InternalLogRecord {
+                    collection_id,
+                    log_offset: record.log_offset,
+                    log_ts: idx as i64 + 1,
+                    record,
+                },
+            );
+        }
+
+        let log = Log::InMemory(in_memory_log.clone());
+
+        // Initial compaction to create segments with FTS index
+        let compact_result = Box::pin(compact(
+            system.clone(),
+            collection_id,
+            database_name.clone(),
+            false,
+            HashSet::new(),
+            1,
+            10,
+            1000,
+            50,
+            log.clone(),
+            sysdb.clone(),
+            test_segments.blockfile_provider.clone(),
+            test_segments.hnsw_provider.clone(),
+            test_segments.spann_provider.clone(),
+            dispatcher_handle.clone(),
+            false,
+            None,
+            None,
+            None,
+        ))
+        .await;
+        assert!(compact_result.is_ok());
+
+        // Get the CAS after initial compaction
+        let old_cas = sysdb
+            .get_collection_with_segments(None, collection_id)
+            .await
+            .expect("Collection and segment information should be present");
+
+        println!(
+            "Collection log position after initial compact: {}",
+            old_cas.collection.log_position
+        );
+
+        // Query to verify FTS works before rebuild
+        let filter = Filter {
+            query_ids: None,
+            where_clause: Some(Where::Document(DocumentExpression {
+                operator: DocumentOperator::Contains,
+                pattern: "fox".to_string(),
+            })),
+        };
+
+        let fetch_log = FetchLogOperator {
+            log_client: log.clone(),
+            batch_size: 50,
+            start_log_offset_id: u64::try_from(old_cas.collection.log_position + 1)
+                .unwrap_or_default(),
+            maximum_fetch_count: None,
+            collection_uuid: old_cas.collection.collection_id,
+            tenant: old_cas.collection.tenant.clone(),
+            database_name: database_name.clone(),
+            fetch_log_concurrency: 10,
+            fragment_fetcher: None,
+        };
+
+        let limit = Limit {
+            offset: 0,
+            limit: None,
+        };
+
+        let project = Projection {
+            document: true,
+            embedding: false,
+            metadata: false,
+        };
+
+        let get_orchestrator = GetOrchestrator::new(
+            test_segments.blockfile_provider.clone(),
+            dispatcher_handle.clone(),
+            1000,
+            old_cas.clone(),
+            fetch_log.clone(),
+            filter.clone(),
+            limit.clone(),
+            project.clone(),
+            None,
+        );
+
+        let old_results = get_orchestrator
+            .run(system.clone())
+            .await
+            .expect("Get orchestrator should not fail");
+
+        // Should find records with "fox" in the document
+        println!(
+            "Records found before rebuild: {:?}",
+            old_results.result.records.len()
+        );
+        for record in &old_results.result.records {
+            println!("Found record: id={}, doc={:?}", record.id, record.document);
+        }
+        // Note: We have 2 documents with "fox" (ids 1 and 4), but FTS may not index id 1 due to compaction timing
+        assert_eq!(
+            old_results.result.records.len(),
+            1,
+            "Should find exactly 1 record with 'fox'"
+        );
+        assert_eq!(old_results.result.records[0].id, "id_4", "Should find id_4");
+
+        // Now perform a metadata-only rebuild
+        let metadata_only_scopes = HashSet::from([chroma_types::SegmentScope::METADATA]);
+        let rebuild_result = Box::pin(compact(
+            system.clone(),
+            collection_id,
+            database_name.clone(),
+            true,
+            metadata_only_scopes,
+            1,
+            10,
+            10000,
+            1000,
+            log.clone(),
+            sysdb.clone(),
+            test_segments.blockfile_provider.clone(),
+            test_segments.hnsw_provider.clone(),
+            test_segments.spann_provider.clone(),
+            dispatcher_handle.clone(),
+            false,
+            None,
+            None,
+            None,
+        ))
+        .await;
+        assert!(rebuild_result.is_ok());
+
+        // Get the new CAS after rebuild
+        let new_cas = sysdb
+            .get_collection_with_segments(None, collection_id)
+            .await
+            .expect("Collection and segment information should be present");
+
+        // Create new fetch log operator with updated position
+        let fetch_log_new = FetchLogOperator {
+            log_client: log.clone(),
+            batch_size: 50,
+            start_log_offset_id: u64::try_from(new_cas.collection.log_position + 1)
+                .unwrap_or_default(),
+            maximum_fetch_count: None,
+            collection_uuid: new_cas.collection.collection_id,
+            tenant: new_cas.collection.tenant.clone(),
+            database_name: database_name.clone(),
+            fetch_log_concurrency: 10,
+            fragment_fetcher: None,
+        };
+
+        // Query again to verify FTS still works after rebuild
+        let get_orchestrator_new = GetOrchestrator::new(
+            test_segments.blockfile_provider.clone(),
+            dispatcher_handle.clone(),
+            1000,
+            new_cas.clone(),
+            fetch_log_new,
+            filter,
+            limit,
+            project,
+            None,
+        );
+
+        let new_results = get_orchestrator_new
+            .run(system)
+            .await
+            .expect("Get orchestrator should not fail after rebuild");
+
+        // FTS index should still work and return the same results
+        println!(
+            "Records found after rebuild: {:?}",
+            new_results.result.records.len()
+        );
+        for record in &new_results.result.records {
+            println!("Found record: id={}, doc={:?}", record.id, record.document);
+        }
+
+        // The key test: FTS index should not be empty after metadata rebuild
+        assert_eq!(
+            new_results.result.records.len(),
+            1,
+            "Should find exactly 1 record after rebuild"
+        );
+        assert_eq!(
+            new_results.result.records[0].id, "id_4",
+            "Should still find id_4 after rebuild"
+        );
+
+        // Verify the exact same records are found before and after rebuild
+        assert_eq!(
+            old_results.result.records.len(),
+            new_results.result.records.len(),
+            "Should find the same number of records before and after rebuild"
+        );
+        assert_eq!(
+            old_results.result.records[0].id, new_results.result.records[0].id,
+            "Should find the same record ID before and after rebuild"
+        );
+        assert_eq!(
+            old_results.result.records[0].document, new_results.result.records[0].document,
+            "Should find the same document content before and after rebuild"
+        );
+    }
+
     #[tokio::test]
     async fn test_rebuild() {
         let config = RootConfig::default();
diff --git a/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs b/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs
index 57b6159bb01..37c81f717f5 100644
--- a/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs
+++ b/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs
@@ -51,12 +51,17 @@ use crate::execution::{
             SourceRecordSegmentError, SourceRecordSegmentInput, SourceRecordSegmentOperator,
             SourceRecordSegmentOutput,
         },
+        source_record_segment_v2::{
+            SourceRecordSegmentV2Error, SourceRecordSegmentV2Input, SourceRecordSegmentV2Operator,
+            SourceRecordSegmentV2Output,
+        },
+    },
+    orchestration::compact::{
+        CollectionCompactInfo, CompactWriters, CompactionContext, CompactionContextError,
+        ExecutionState,
     },
-    orchestration::compact::CompactionContextError,
 };

-use super::compact::{CollectionCompactInfo, CompactWriters, CompactionContext, ExecutionState};
-
 #[derive(Error, Debug)]
 pub enum LogFetchOrchestratorError {
     #[error("Operation aborted because resources exhausted")]
@@ -97,6 +102,8 @@ pub enum LogFetchOrchestratorError {
     SpannSegment(#[from] SpannSegmentWriterError),
     #[error("Error sourcing record segment: {0}")]
     SourceRecordSegment(#[from] SourceRecordSegmentError),
+    #[error("Error sourcing record segment v2: {0}")]
+    SourceRecordSegmentV2(#[from] SourceRecordSegmentV2Error),
     #[error("Could not count current segment: {0}")]
     CountError(Box<dyn chroma_error::ChromaError>),
 }
@@ -133,6 +140,7 @@ impl ChromaError for LogFetchOrchestratorError {
                 Self::RecvError(_) => true,
                 Self::SpannSegment(e) => e.should_trace_error(),
                 Self::SourceRecordSegment(e) => e.should_trace_error(),
+                Self::SourceRecordSegmentV2(e) => e.should_trace_error(),
                 Self::CountError(e) => e.should_trace_error(),
             }
         }
@@ -472,17 +480,34 @@ impl Handler<TaskResult<GetCollectionAndSegmentsOutput, GetCollectionAndSegments
         };

         let log_task = if self.context.is_rebuild {
-            wrap(
-                Box::new(SourceRecordSegmentOperator {}),
-                SourceRecordSegmentInput {
-                    record_segment_reader: record_reader.clone(),
-                },
-                ctx.receiver(),
-                self.context
-                    .orchestrator_context
-                    .task_cancellation_token
-                    .clone(),
-            )
+            // TODO(tanujnay112): Remove this once we've fully baked in SourceRecordSegmentV2Operator
+            if self.context.is_full_rebuild() {
+                wrap(
+                    Box::new(SourceRecordSegmentOperator::new()),
+                    SourceRecordSegmentInput {
+                        record_segment_reader: record_reader.clone(),
+                    },
+                    ctx.receiver(),
+                    self.context
+                        .orchestrator_context
+                        .task_cancellation_token
+                        .clone(),
+                )
+            } else {
+                wrap(
+                    Box::new(SourceRecordSegmentV2Operator::new(
+                        self.context.max_partition_size,
+                    )),
+                    SourceRecordSegmentV2Input {
+                        record_segment_reader: record_reader.clone(),
+                    },
+                    ctx.receiver(),
+                    self.context
+                        .orchestrator_context
+                        .task_cancellation_token
+                        .clone(),
+                )
+            }
         } else {
             let database_name = match chroma_types::DatabaseName::new(collection.database.clone()) {
                 Some(name) => name,
@@ -678,11 +703,8 @@ impl Handler<TaskResult<GetCollectionAndSegmentsOutput, GetCollectionAndSegments
         };

         let writers = CompactWriters {
-            // If we are rebuilding but not applying to the record segment,
-            // we should still read the record segment to get its offset ids.
-            record_reader: record_reader
-                .clone()
-                .filter(|_| !self.context.is_full_rebuild()),
+            // No record reader when rebuilding
+            record_reader: record_reader.clone().filter(|_| !self.context.is_rebuild),
             metadata_writer,
             record_writer,
             vector_writer,
@@ -866,6 +888,96 @@ impl Handler<TaskResult<SourceRecordSegmentOutput, SourceRecordSegmentError>>
     }
 }

+#[async_trait]
+impl Handler<TaskResult<SourceRecordSegmentV2Output, SourceRecordSegmentV2Error>>
+    for LogFetchOrchestrator
+{
+    type Result = ();
+
+    async fn handle(
+        &mut self,
+        message: TaskResult<SourceRecordSegmentV2Output, SourceRecordSegmentV2Error>,
+        ctx: &ComponentContext<Self>,
+    ) {
+        let output = match self.ok_or_terminate(message.into_inner(), ctx).await {
+            Some(output) => output,
+            None => return,
+        };
+
+        tracing::info!(
+            "Sourced and materialized {} records in {} partitions",
+            output.total_records,
+            output.partitions.len()
+        );
+
+        // Update total records count
+        let collection_info = match self.context.get_collection_info_mut() {
+            Ok(info) => info,
+            Err(err) => {
+                self.terminate_with_result(Err(err.into()), ctx).await;
+                return;
+            }
+        };
+        collection_info.collection.total_records_post_compaction = output.total_records as u64;
+
+        // If no records, terminate early
+        if output.partitions.is_empty() {
+            let collection_info = match self.context.get_collection_info() {
+                Ok(info) => info,
+                Err(err) => {
+                    self.terminate_with_result(Err(err.into()), ctx).await;
+                    return;
+                }
+            };
+            self.terminate_with_result(
+                Ok(Success::new(vec![], collection_info.clone()).into()),
+                ctx,
+            )
+            .await;
+            return;
+        }
+
+        // Update handler to work with MaterializeLogOutput directly
+        self.num_uncompleted_materialization_tasks = 0;
+        for partition in output.partitions {
+            if partition.result.has_backfill() {
+                self.has_backfill = true;
+            }
+
+            if !partition.result.is_empty() {
+                self.materialized_outputs.push(partition);
+            }
+        }
+
+        // Complete the rebuild flow
+        let collection_info = match self.context.collection_info.take() {
+            Some(info) => info,
+            None => {
+                self.terminate_with_result(
+                    Err(LogFetchOrchestratorError::InvariantViolation(
+                        "self.collection_info not set",
+                    )),
+                    ctx,
+                )
+                .await;
+                return;
+            }
+        };
+
+        let materialized = std::mem::take(&mut self.materialized_outputs);
+        if self.has_backfill {
+            self.terminate_with_result(
+                Ok(RequireFunctionBackfill::new(materialized, collection_info).into()),
+                ctx,
+            )
+            .await;
+            return;
+        }
+        self.terminate_with_result(Ok(Success::new(materialized, collection_info).into()), ctx)
+            .await;
+    }
+}
+
 #[async_trait]
 impl Handler<TaskResult<PartitionOutput, PartitionError>> for LogFetchOrchestrator {
     type Result = ();
@@ -921,6 +1033,7 @@ impl Handler<TaskResult<MaterializeLogOutput, MaterializeLogOperatorError>>
                     return;
                 }
             };
+
             let materialized = std::mem::take(&mut self.materialized_outputs);
             if self.has_backfill {
                 self.terminate_with_result(
PATCH

echo "Patch applied successfully"
