#!/bin/bash
set -e

cd /workspace/chroma

# Apply the gold patch for PR #6699
cat <<'PATCH' | git apply -
diff --git a/rust/segment/src/distributed_hnsw.rs b/rust/segment/src/distributed_hnsw.rs
index aa6196971ac..8c911a25c51 100644
--- a/rust/segment/src/distributed_hnsw.rs
+++ b/rust/segment/src/distributed_hnsw.rs
@@ -322,6 +322,12 @@ impl DistributedHNSWSegmentReader {
         DistributedHNSWSegmentReader { index, id }
     }

+    pub fn get_all_offset_ids(&self) -> Result<Vec<usize>, Box<dyn ChromaError>> {
+        let hnsw_index = &self.index.inner.read().hnsw_index;
+        let (offset_ids, _sizes) = hnsw_index.get_all_ids()?;
+        Ok(offset_ids)
+    }
+
     pub async fn from_segment(
         collection: &Collection,
         segment: &Segment,
diff --git a/rust/worker/src/execution/operators/source_record_segment.rs b/rust/worker/src/execution/operators/source_record_segment.rs
index 9454d547e69..feb603bd5c4 100644
--- a/rust/worker/src/execution/operators/source_record_segment.rs
+++ b/rust/worker/src/execution/operators/source_record_segment.rs
@@ -66,7 +66,7 @@ impl Operator<SourceRecordSegmentInput, SourceRecordSegmentOutput> for SourceRec
                                     meta.into_iter().map(|(k, v)| (k, v.into())).collect()
                                 }),
                                 document: rec.document.map(ToString::to_string),
-                                operation: chroma_types::Operation::Add,
+                                operation: chroma_types::Operation::Upsert,
                             },
                         })
                     })
@@ -124,7 +124,7 @@ mod tests {
         for (offset, (record, _)) in source_output.iter().enumerate() {
             assert_eq!(record.log_offset, offset as i64 + 1);
             assert_eq!(record.record.id, int_as_id(offset + 1));
-            assert_eq!(record.record.operation, Operation::Add);
+            assert_eq!(record.record.operation, Operation::Upsert);
         }
     }
 }
diff --git a/rust/worker/src/execution/orchestration/apply_logs_orchestrator.rs b/rust/worker/src/execution/orchestration/apply_logs_orchestrator.rs
index fa6c0da030a..7a25ca6a7ee 100644
--- a/rust/worker/src/execution/orchestration/apply_logs_orchestrator.rs
+++ b/rust/worker/src/execution/orchestration/apply_logs_orchestrator.rs
@@ -364,7 +364,7 @@ impl ApplyLogsOrchestrator {
             }
         };
         let collection = collection_info.collection.clone();
-        let collection_logical_size_bytes = if self.context.is_rebuild {
+        let collection_logical_size_bytes = if self.context.is_full_rebuild() {
             match u64::try_from(self.collection_logical_size_delta_bytes) {
                 Ok(size_bytes) => size_bytes,
                 _ => {
diff --git a/rust/worker/src/execution/orchestration/compact.rs b/rust/worker/src/execution/orchestration/compact.rs
index 4f426ccac88..bb6fd8154bb 100644
--- a/rust/worker/src/execution/orchestration/compact.rs
+++ b/rust/worker/src/execution/orchestration/compact.rs
@@ -183,6 +183,10 @@ impl CompactionContext {
         self.apply_segment_scopes.is_empty() || self.apply_segment_scopes.contains(scope)
     }

+    pub fn is_full_rebuild(&self) -> bool {
+        self.is_rebuild && self.scope_is_active(&chroma_types::SegmentScope::RECORD)
+    }
+
     /// Create an empty output context for attached function orchestrator
     /// This creates a new context with an empty collection_info OnceCell
     fn clone_for_new_collection(&self) -> Self {
@@ -405,6 +409,7 @@ impl CompactionContext {
             collection_id,
             database_name,
             self.is_rebuild || is_getting_compacted_logs,
+            self.apply_segment_scopes.clone(),
             self.fetch_log_batch_size,
             self.fetch_log_concurrency,
             self.max_compaction_size,
@@ -1006,7 +1011,10 @@ mod tests {
         test::{add_delete_generator, LogGenerator},
         Log,
     };
-	use chroma_segment::{spann_provider::SpannProvider, test::TestDistributedSegment};
+	use chroma_segment::{
+	    blockfile_record::RecordSegmentReader, distributed_hnsw::DistributedHNSWSegmentReader,
+	    spann_provider::SpannProvider, test::TestDistributedSegment,
+	};
     use chroma_storage::{local::LocalStorage, Storage};
     use chroma_sysdb::{SysDb, TestSysDb};
     use chroma_system::{ComponentHandle, Dispatcher, DispatcherConfig, Orchestrator, System};
@@ -1015,6 +1023,7 @@ mod tests {
         Collection, DocumentExpression, DocumentOperator, MetadataExpression, PrimitiveOperator,
         Segment, SegmentUuid, Where,
     };
+	use futures::TryStreamExt;
     use regex::Regex;
     use tempfile;

@@ -1026,6 +1035,59 @@ mod tests {
     use super::{compact, CompactionContext, CompactionResponse, LogFetchOrchestratorResponse};
     use crate::execution::orchestration::register_orchestrator::CollectionRegisterInfo;

+	#[cfg(test)]
+	async fn check_offset_ids_match(
+	    collection: &Collection,
+	    vector_segment: &Segment,
+	    record_segment: &Segment,
+	    hnsw_provider: HnswIndexProvider,
+	    blockfile_provider: &BlockfileProvider,
+	) {
+	    // Get offset IDs from vector segment
+	    let vector_reader = DistributedHNSWSegmentReader::from_segment(
+	        collection,
+	        vector_segment,
+	        collection.dimension.unwrap() as usize,
+	        hnsw_provider,
+	    )
+	    .await
+	    .expect("Should create vector reader");
+
+	    let mut vector_offset_ids = vector_reader
+	        .get_all_offset_ids()
+	        .expect("Should get all IDs from HNSW index");
+	    vector_offset_ids.sort();
+
+	    // Get offset IDs from record segment
+	    let record_reader = Box::pin(RecordSegmentReader::from_segment(
+	        record_segment,
+	        blockfile_provider,
+	        None,
+	    ))
+	    .await
+	    .expect("Should create record reader");
+
+	    let record_data: Vec<_> = record_reader
+	        .get_data_stream(..)
+	        .await
+	        .try_collect()
+	        .await
+	        .expect("Should read all records");
+
+	    let mut record_offset_ids: Vec<usize> = record_data
+	        .into_iter()
+	        .map(|(offset_id, _data)| offset_id as usize)
+	        .collect();
+	    record_offset_ids.sort();
+
+	    // Assert they match
+	    assert_eq!(vector_offset_ids.len(), record_offset_ids.len());
+	    assert_eq!(
+	        vector_offset_ids, record_offset_ids,
+	        "Vector and record segment offset IDs should match after vector-only rebuild"
+	    );
+	}
+
     async fn get_all_records(
         system: &System,
         dispatcher_handle: &ComponentHandle<Dispatcher>,
@@ -1310,6 +1372,7 @@ mod tests {
         let mut sysdb = SysDb::Test(TestSysDb::new());
         let test_segments = TestDistributedSegment::new().await;
         let collection_id = test_segments.collection.collection_id;
+	let collection_for_reader = test_segments.collection.clone();
         let database_name =
             chroma_types::DatabaseName::new(test_segments.collection.database.clone())
                 .expect("database name should be valid");
@@ -1347,7 +1410,7 @@ mod tests {
                     },
                 )
             });
-	let log = Log::InMemory(in_memory_log);
+	let log = Log::InMemory(in_memory_log.clone());

         // Initial compaction to create segments
         let compact_result = Box::pin(compact(
@@ -1374,6 +1437,57 @@ mod tests {
         .await;
         assert!(compact_result.is_ok());

+	let delete_ids = [75, 77, 79, 83];
+	for (idx, rec_id) in delete_ids.iter().enumerate() {
+	    let del_record = chroma_types::LogRecord {
+	        log_offset: 120 + idx as i64,
+	        record: chroma_types::OperationRecord {
+	            id: chroma_log::test::int_as_id(*rec_id),
+	            embedding: None,
+	            encoding: None,
+	            metadata: None,
+	            document: None,
+	            operation: chroma_types::Operation::Delete,
+	        },
+	    };
+
+	    in_memory_log.add_log(
+	        collection_id,
+	        InternalLogRecord {
+	            collection_id,
+	            log_offset: del_record.log_offset,
+	            log_ts: del_record.log_offset,
+	            record: del_record,
+	        },
+	    );
+	}
+
+	let log = Log::InMemory(in_memory_log.clone());
+
+	let compact_result = Box::pin(compact(
+	    system.clone(),
+	    collection_id,
+	    database_name.clone(),
+	    false,
+	    HashSet::new(),
+	    1,
+	    10,
+	    1000,
+	    50,
+	    log.clone(),
+	    sysdb.clone(),
+	    test_segments.blockfile_provider.clone(),
+	    test_segments.hnsw_provider.clone(),
+	    test_segments.spann_provider.clone(),
+	    dispatcher_handle.clone(),
+	    false,
+	    None,
+	    None,
+	    None,
+	))
+	.await;
+	assert!(compact_result.is_ok());
+
         let old_cas = sysdb
             .get_collection_with_segments(None, collection_id)
             .await
@@ -1390,6 +1504,15 @@ mod tests {
         .await;
         assert!(!old_records.is_empty());

+	Box::pin(check_offset_ids_match(
+	    &collection_for_reader,
+	    &old_cas.vector_segment,
+	    &old_cas.record_segment,
+	    test_segments.hnsw_provider.clone(),
+	    &test_segments.blockfile_provider,
+	))
+	.await;
+
         // Rebuild ONLY the vector segment
         let vector_only_scopes = HashSet::from([chroma_types::SegmentScope::VECTOR]);
         let rebuild_result = Box::pin(compact(
@@ -1427,13 +1550,32 @@ mod tests {
         // Version file path should be updated
         let version_suffix_re = Regex::new(r"/\\d+$").unwrap();
         let expected_version_file = version_suffix_re
-	    .replace(&old_cas.collection.version_file_path.clone().unwrap(), "/2")
+	    .replace(&old_cas.collection.version_file_path.clone().unwrap(), "/3")
             .to_string();
         assert_eq!(
             new_cas.collection.version_file_path,
             Some(expected_version_file)
         );

+	// Verify offset IDs match after vector-only rebuild
+	Box::pin(check_offset_ids_match(
+	    &collection_for_reader,
+	    &new_cas.vector_segment,
+	    &new_cas.record_segment,
+	    test_segments.hnsw_provider.clone(),
+	    &test_segments.blockfile_provider,
+	))
+	.await;
+
+	let mut expected_new_collection = old_cas.collection.clone();
+	expected_new_collection.version += 1;
+	expected_new_collection.version_file_path = Some(
+	    version_suffix_re
+	        .replace(&old_cas.collection.version_file_path.clone().unwrap(), "/3")
+	        .to_string(),
+	);
+	assert_eq!(new_cas.collection, expected_new_collection);
+
         // Record count and size should be preserved
         assert_eq!(
             new_cas.collection.total_records_post_compaction,
diff --git a/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs b/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs
index 8954adbfe17..57b6159bb01 100644
--- a/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs
+++ b/rust/worker/src/execution/orchestration/log_fetch_orchestrator.rs
@@ -298,6 +298,7 @@ impl LogFetchOrchestrator {
         collection_id: CollectionUuid,
         database_name: chroma_types::DatabaseName,
         is_rebuild: bool,
+        apply_segment_scopes: std::collections::HashSet<chroma_types::SegmentScope>,
         fetch_log_batch_size: u32,
         fetch_log_concurrency: usize,
         max_compaction_size: usize,
@@ -313,7 +314,7 @@ impl LogFetchOrchestrator {
     ) -> Self {
         let context = CompactionContext::new(
             is_rebuild,
-	    std::collections::HashSet::new(),
+	    apply_segment_scopes,
             fetch_log_batch_size,
             fetch_log_concurrency,
             max_compaction_size,
@@ -677,7 +678,11 @@ impl Handler<TaskResult<GetCollectionAndSegmentsOutput, GetCollectionAndSegments
         };

         let writers = CompactWriters {
-	    record_reader: record_reader.clone().filter(|_| !self.context.is_rebuild),
+	    // If we are rebuilding but not applying to the record segment,
+	    // we should still read the record segment to get its offset ids.
+	    record_reader: record_reader
+	        .clone()
+	        .filter(|_| !self.context.is_full_rebuild()),
             metadata_writer,
             record_writer,
             vector_writer,
PATCH

# Verify the patch was applied by checking for a distinctive line
if !grep -q "is_full_rebuild" rust/worker/src/execution/orchestration/compact.rs; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
