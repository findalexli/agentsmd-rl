#!/bin/bash
set -e

cd /workspace/chroma

# Check if already applied
if grep -q "shard_index = 0" rust/types/src/execution/operator.rs 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/idl/chromadb/proto/query_executor.proto b/idl/chromadb/proto/query_executor.proto
index f28e37f6e4c..9f4c9da58cc 100644
--- a/idl/chromadb/proto/query_executor.proto
+++ b/idl/chromadb/proto/query_executor.proto
@@ -11,6 +11,13 @@ message ScanOperator {
     Segment knn = 5;
     Segment metadata = 6;
     Segment record = 7;
+    // Which shard this worker is responsible for querying.
+    uint32 shard_index = 8;
+    // Total number of shards for the collection. 0 is treated as 1 (unsharded).
+    uint32 num_shards = 9;
+    // Upper bound log offset scouted by the frontend. 0 means the worker
+    // should scout independently (legacy / backward-compatible path).
+    int64 log_upper_bound_offset = 10;
 }

 message FilterOperator {
diff --git a/rust/frontend/src/impls/in_memory_frontend.rs b/rust/frontend/src/impls/in_memory_frontend.rs
index 04c21e7fdbb..9d5efaac1cc 100644
--- a/rust/frontend/src/impls/in_memory_frontend.rs
+++ b/rust/frontend/src/impls/in_memory_frontend.rs
@@ -540,6 +540,9 @@ impl InMemoryFrontend {
                         vector_segment: collection.vector_segment.clone(),
                         record_segment: collection.record_segment.clone(),
                     },
+                    shard_index: 0,
+                    num_shards: 1,
+                    log_upper_bound_offset: 0,
                 },
                 read_level: request.read_level,
             })
@@ -591,6 +594,9 @@ impl InMemoryFrontend {
                         vector_segment: collection.vector_segment.clone(),
                         record_segment: collection.record_segment.clone(),
                     },
+                    shard_index: 0,
+                    num_shards: 1,
+                    log_upper_bound_offset: 0,
                 },
                 filter,
                 limit: Limit { offset, limit },
@@ -664,6 +670,9 @@ impl InMemoryFrontend {
                             vector_segment: collection.vector_segment.clone(),
                             record_segment: collection.record_segment.clone(),
                         },
+                        shard_index: 0,
+                        num_shards: 1,
+                        log_upper_bound_offset: 0,
                     },
                     filter,
                     knn: KnnBatch {
diff --git a/rust/frontend/src/impls/service_based_frontend.rs b/rust/frontend/src/impls/service_based_frontend.rs
index 66cac117ad0..f5cc68c195d 100644
--- a/rust/frontend/src/impls/service_based_frontend.rs
+++ b/rust/frontend/src/impls/service_based_frontend.rs
@@ -1237,6 +1237,9 @@ impl ServiceBasedFrontend {
                 .get(Get {
                     scan: Scan {
                         collection_and_segments,
+                        shard_index: 0,
+                        num_shards: 1,
+                        log_upper_bound_offset: 0,
                     },
                     filter,
                     limit: Limit { offset: 0, limit },
@@ -1451,6 +1454,9 @@ impl ServiceBasedFrontend {
             .count(Count {
                 scan: Scan {
                     collection_and_segments,
+                    shard_index: 0,
+                    num_shards: 1,
+                    log_upper_bound_offset: 0,
                 },
                 read_level,
             })
@@ -1638,6 +1644,9 @@ impl ServiceBasedFrontend {
             .get(Get {
                 scan: Scan {
                     collection_and_segments,
+                    shard_index: 0,
+                    num_shards: 1,
+                    log_upper_bound_offset: 0,
                 },
                 filter: Filter {
                     query_ids: ids,
@@ -1792,6 +1801,9 @@ impl ServiceBasedFrontend {
             .knn(Knn {
                 scan: Scan {
                     collection_and_segments,
+                    shard_index: 0,
+                    num_shards: 1,
+                    log_upper_bound_offset: 0,
                 },
                 filter: Filter {
                     query_ids: ids,
@@ -1989,6 +2001,9 @@ impl ServiceBasedFrontend {
         let search_plan = Search {
             scan: Scan {
                 collection_and_segments,
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             payloads: request.searches,
             read_level: request.read_level,
diff --git a/rust/segment/src/sqlite_metadata.rs b/rust/segment/src/sqlite_metadata.rs
index 6a95e220867..7111b527a78 100644
--- a/rust/segment/src/sqlite_metadata.rs
+++ b/rust/segment/src/sqlite_metadata.rs
@@ -966,6 +966,7 @@ impl SqliteMetadataReader {
         Count {
             scan: Scan {
                 collection_and_segments,
+                ..
             },
             ..
         }: Count,
@@ -995,6 +996,7 @@ impl SqliteMetadataReader {
         Get {
             scan: Scan {
                 collection_and_segments,
+                ..
             },
             filter: Filter {
                 query_ids,
@@ -1199,7 +1201,7 @@ mod tests {
             let sqlite_seg_reader = SqliteMetadataReader {
                 db: sqlite_seg_writer.db
             };
-            let plan = Count { scan: Scan { collection_and_segments: test_data.collection_and_segments.clone() }, read_level: ReadLevel::default() };
+            let plan = Count { scan: Scan { collection_and_segments: test_data.collection_and_segments.clone(), shard_index: 0, num_shards: 1, log_upper_bound_offset: 0 }, read_level: ReadLevel::default() };
             let ref_count = ref_seg.count(plan.clone()).expect("Count should not fail").count;
             let sqlite_count = runtime.block_on(sqlite_seg_reader.count(plan)).expect("Count should not fail").count;
             assert_eq!(sqlite_count, ref_count);
@@ -1241,6 +1243,9 @@ mod tests {
             let plan = Get {
                 scan: Scan {
                     collection_and_segments: test_data.collection_and_segments.clone(),
+                    shard_index: 0,
+                    num_shards: 1,
+                    log_upper_bound_offset: 0,
                 },
                 filter: Filter {
                     query_ids: None,
@@ -1338,6 +1343,9 @@ mod tests {
         let plan = Get {
             scan: Scan {
                 collection_and_segments: collection_and_segments.clone(),
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             filter: Filter {
                 query_ids: None,
@@ -1375,6 +1383,9 @@ mod tests {
         let plan2 = Get {
             scan: Scan {
                 collection_and_segments: collection_and_segments.clone(),
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             filter: Filter {
                 query_ids: None,
@@ -1485,6 +1496,9 @@ mod tests {
         let fts_plan = Get {
             scan: Scan {
                 collection_and_segments: collection_and_segments.clone(),
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             filter: Filter {
                 query_ids: None,
@@ -1514,6 +1528,9 @@ mod tests {
         let metadata_plan = Get {
             scan: Scan {
                 collection_and_segments: collection_and_segments.clone(),
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             filter: Filter {
                 query_ids: None,
@@ -1543,6 +1560,9 @@ mod tests {
         let hybrid_plan = Get {
             scan: Scan {
                 collection_and_segments: collection_and_segments.clone(),
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             filter: Filter {
                 query_ids: None,
@@ -1600,6 +1620,9 @@ mod tests {
         Get {
             scan: Scan {
                 collection_and_segments: cas.clone(),
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             filter: Filter {
                 query_ids: None,
@@ -2006,6 +2029,9 @@ mod tests {
         let plan = Get {
             scan: Scan {
                 collection_and_segments: cas.clone(),
+                shard_index: 0,
+                num_shards: 1,
+                log_upper_bound_offset: 0,
             },
             filter: Filter {
                 query_ids: None,
diff --git a/rust/types/src/execution/operator.rs b/rust/types/src/execution/operator.rs
index f21e699fcb7..a18c648848a 100644
--- a/rust/types/src/execution/operator.rs
+++ b/rust/types/src/execution/operator.rs
@@ -27,12 +27,18 @@ pub type InitialInput = ();
 #[derive(Clone, Debug)]
 pub struct Scan {
     pub collection_and_segments: CollectionAndSegments,
+    pub shard_index: u32,
+    pub num_shards: u32,
+    /// Upper bound log offset scouted by the frontend.
+    /// 0 means the worker should scout independently.
+    pub log_upper_bound_offset: i64,
 }

 impl TryFrom<chroma_proto::ScanOperator> for Scan {
     type Error = QueryConversionError;

     fn try_from(value: chroma_proto::ScanOperator) -> Result<Self, Self::Error> {
+        let num_shards = value.num_shards.max(1);
         Ok(Self {
             collection_and_segments: CollectionAndSegments {
                 collection: value
@@ -52,6 +58,9 @@ impl TryFrom<chroma_proto::ScanOperator> for Scan {
                     .ok_or(QueryConversionError::field("vector segment"))?
                     .try_into()?,
             },
+            shard_index: value.shard_index,
+            num_shards,
+            log_upper_bound_offset: value.log_upper_bound_offset,
         })
     }
 }
@@ -71,6 +80,9 @@ impl TryFrom<Scan> for chroma_proto::ScanOperator {
             knn: Some(value.collection_and_segments.vector_segment.into()),
             metadata: Some(value.collection_and_segments.metadata_segment.into()),
             record: Some(value.collection_and_segments.record_segment.into()),
+            shard_index: value.shard_index,
+            num_shards: value.num_shards,
+            log_upper_bound_offset: value.log_upper_bound_offset,
         })
     }
 }
diff --git a/rust/worker/src/server.rs b/rust/worker/src/server.rs
index d95b07ed85a..7d4b007c7be 100644
--- a/rust/worker/src/server.rs
+++ b/rust/worker/src/server.rs
@@ -957,6 +957,9 @@ mod tests {
                 metadata: None,
                 file_paths: HashMap::new(),
             }),
+            shard_index: 0,
+            num_shards: 1,
+            log_upper_bound_offset: 0,
         }
     }
PATCH

echo "Patch applied successfully"
