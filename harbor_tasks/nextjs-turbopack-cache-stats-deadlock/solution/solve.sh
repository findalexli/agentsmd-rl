#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

CARGO_FILE="turbopack/crates/turbo-tasks-backend/Cargo.toml"
MOD_FILE="turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"

# Idempotency check: if the deadlock fix is already applied, skip
if grep -q 'TaskCacheStats::task_name(inner)' "$MOD_FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbo-tasks-backend/Cargo.toml b/turbopack/crates/turbo-tasks-backend/Cargo.toml
index db082ac9c76804..46f10f5423d18f 100644
--- a/turbopack/crates/turbo-tasks-backend/Cargo.toml
+++ b/turbopack/crates/turbo-tasks-backend/Cargo.toml
@@ -14,7 +14,8 @@ workspace = true

 [features]
 default = []
-print_cache_item_size = ["dep:lzzzz"]
+print_cache_item_size_with_compressed = ["print_cache_item_size", "dep:lzzzz"]
+print_cache_item_size = []
 no_fast_stale = []
 aggregation_update_no_batch = []
 verify_serialization = []
diff --git a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
index 368f887465ac2e..011f8f76547f1c 100644
--- a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
+++ b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
@@ -1053,9 +1053,11 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
         #[derive(Default)]
         struct TaskCacheStats {
             data: usize,
+            #[cfg(feature = "print_cache_item_size_with_compressed")]
             data_compressed: usize,
             data_count: usize,
             meta: usize,
+            #[cfg(feature = "print_cache_item_size_with_compressed")]
             meta_compressed: usize,
             meta_count: usize,
             upper_count: usize,
@@ -1067,8 +1069,36 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
             aggregated_dirty_containers_count: usize,
             output_size: usize,
         }
+        /// Formats a byte size, optionally including the compressed size when the
+        /// `print_cache_item_size_with_compressed` feature is enabled.
+        #[cfg(feature = "print_cache_item_size")]
+        struct FormatSizes {
+            size: usize,
+            #[cfg(feature = "print_cache_item_size_with_compressed")]
+            compressed_size: usize,
+        }
+        #[cfg(feature = "print_cache_item_size")]
+        impl std::fmt::Display for FormatSizes {
+            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
+                use turbo_tasks::util::FormatBytes;
+                #[cfg(feature = "print_cache_item_size_with_compressed")]
+                {
+                    write!(
+                        f,
+                        "{} ({} compressed)",
+                        FormatBytes(self.size),
+                        FormatBytes(self.compressed_size)
+                    )
+                }
+                #[cfg(not(feature = "print_cache_item_size_with_compressed"))]
+                {
+                    write!(f, "{}", FormatBytes(self.size))
+                }
+            }
+        }
         #[cfg(feature = "print_cache_item_size")]
         impl TaskCacheStats {
+            #[cfg(feature = "print_cache_item_size_with_compressed")]
             fn compressed_size(data: &[u8]) -> Result<usize> {
                 Ok(lzzzz::lz4::Compressor::new()?.next_to_vec(
                     data,
@@ -1079,13 +1109,19 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {

             fn add_data(&mut self, data: &[u8]) {
                 self.data += data.len();
-                self.data_compressed += Self::compressed_size(data).unwrap_or(0);
+                #[cfg(feature = "print_cache_item_size_with_compressed")]
+                {
+                    self.data_compressed += Self::compressed_size(data).unwrap_or(0);
+                }
                 self.data_count += 1;
             }

             fn add_meta(&mut self, data: &[u8]) {
                 self.meta += data.len();
-                self.meta_compressed += Self::compressed_size(data).unwrap_or(0);
+                #[cfg(feature = "print_cache_item_size_with_compressed")]
+                {
+                    self.meta_compressed += Self::compressed_size(data).unwrap_or(0);
+                }
                 self.meta_count += 1;
             }

@@ -1106,6 +1142,73 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
                         .unwrap_or(0);
                 }
             }
+
+            /// Returns the task name used as the stats grouping key.
+            fn task_name(storage: &TaskStorage) -> String {
+                storage
+                    .get_persistent_task_type()
+                    .map(|t| t.to_string())
+                    .unwrap_or_else(|| "<unknown>".to_string())
+            }
+
+            /// Returns the primary sort key: compressed total when
+            /// `print_cache_item_size_with_compressed` is enabled, raw total otherwise.
+            fn sort_key(&self) -> usize {
+                #[cfg(feature = "print_cache_item_size_with_compressed")]
+                {
+                    self.data_compressed + self.meta_compressed
+                }
+                #[cfg(not(feature = "print_cache_item_size_with_compressed"))]
+                {
+                    self.data + self.meta
+                }
+            }
+
+            fn format_total(&self) -> FormatSizes {
+                FormatSizes {
+                    size: self.data + self.meta,
+                    #[cfg(feature = "print_cache_item_size_with_compressed")]
+                    compressed_size: self.data_compressed + self.meta_compressed,
+                }
+            }
+
+            fn format_data(&self) -> FormatSizes {
+                FormatSizes {
+                    size: self.data,
+                    #[cfg(feature = "print_cache_item_size_with_compressed")]
+                    compressed_size: self.data_compressed,
+                }
+            }
+
+            fn format_avg_data(&self) -> FormatSizes {
+                FormatSizes {
+                    size: self.data.checked_div(self.data_count).unwrap_or(0),
+                    #[cfg(feature = "print_cache_item_size_with_compressed")]
+                    compressed_size: self
+                        .data_compressed
+                        .checked_div(self.data_count)
+                        .unwrap_or(0),
+                }
+            }
+
+            fn format_meta(&self) -> FormatSizes {
+                FormatSizes {
+                    size: self.meta,
+                    #[cfg(feature = "print_cache_item_size_with_compressed")]
+                    compressed_size: self.meta_compressed,
+                }
+            }
+
+            fn format_avg_meta(&self) -> FormatSizes {
+                FormatSizes {
+                    size: self.meta.checked_div(self.meta_count).unwrap_or(0),
+                    #[cfg(feature = "print_cache_item_size_with_compressed")]
+                    compressed_size: self
+                        .meta_compressed
+                        .checked_div(self.meta_count)
+                        .unwrap_or(0),
+                }
+            }
         }
         #[cfg(feature = "print_cache_item_size")]
         let task_cache_stats: Mutex<FxHashMap<_, TaskCacheStats>> =
@@ -1128,9 +1231,7 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
                         #[cfg(feature = "print_cache_item_size")]
                         {
                             let mut stats = task_cache_stats.lock();
-                            let entry = stats
-                                .entry(self.get_task_name(task_id, turbo_tasks))
-                                .or_default();
+                            let entry = stats.entry(TaskCacheStats::task_name(inner)).or_default();
                             match category {
                                 SpecificTaskDataCategory::Meta => entry.add_meta(&encoded),
                                 SpecificTaskDataCategory::Data => entry.add_data(&encoded),
@@ -1157,10 +1258,10 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
             let encode_data = inner.flags.data_modified();

             #[cfg(feature = "print_cache_item_size")]
-            if encode_meta {
+            if encode_data || encode_meta {
                 task_cache_stats
                     .lock()
-                    .entry(self.get_task_name(task_id, turbo_tasks))
+                    .entry(TaskCacheStats::task_name(inner))
                     .or_default()
                     .add_counts(inner);
             }
@@ -1220,23 +1321,22 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
                     use crate::utils::markdown_table::print_markdown_table;

                     task_cache_stats.sort_unstable_by(|(key_a, stats_a), (key_b, stats_b)| {
-                        (stats_b.data_compressed + stats_b.meta_compressed, key_b)
-                            .cmp(&(stats_a.data_compressed + stats_a.meta_compressed, key_a))
+                        (stats_b.sort_key(), key_b).cmp(&(stats_a.sort_key(), key_a))
                     });
+
                     println!(
-                        "Task cache stats: {} ({})",
-                        FormatBytes(
-                            task_cache_stats
-                                .iter()
-                                .map(|(_, s)| s.data_compressed + s.meta_compressed)
-                                .sum::<usize>()
-                        ),
-                        FormatBytes(
-                            task_cache_stats
+                        "Task cache stats: {}",
+                        FormatSizes {
+                            size: task_cache_stats
                                 .iter()
                                 .map(|(_, s)| s.data + s.meta)
+                                .sum::<usize>(),
+                            #[cfg(feature = "print_cache_item_size_with_compressed")]
+                            compressed_size: task_cache_stats
+                                .iter()
+                                .map(|(_, s)| s.data_compressed + s.meta_compressed)
                                 .sum::<usize>()
-                        )
+                        },
                     );

                     print_markdown_table(
@@ -1262,47 +1362,13 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
                         |(task_desc, stats)| {
                             [
                                 task_desc.to_string(),
-                                format!(
-                                    " {} ({})",
-                                    FormatBytes(stats.data_compressed + stats.meta_compressed),
-                                    FormatBytes(stats.data + stats.meta)
-                                ),
-                                format!(
-                                    " {} ({})",
-                                    FormatBytes(stats.data_compressed),
-                                    FormatBytes(stats.data)
-                                ),
-                                format!(" {} x", stats.data_count,),
-                                format!(
-                                    "{} ({})",
-                                    FormatBytes(
-                                        stats
-                                            .data_compressed
-                                            .checked_div(stats.data_count)
-                                            .unwrap_or(0)
-                                    ),
-                                    FormatBytes(
-                                        stats.data.checked_div(stats.data_count).unwrap_or(0)
-                                    ),
-                                ),
-                                format!(
-                                    " {} ({})",
-                                    FormatBytes(stats.meta_compressed),
-                                    FormatBytes(stats.meta)
-                                ),
-                                format!(" {} x", stats.meta_count,),
-                                format!(
-                                    "{} ({})",
-                                    FormatBytes(
-                                        stats
-                                            .meta_compressed
-                                            .checked_div(stats.meta_count)
-                                            .unwrap_or(0)
-                                    ),
-                                    FormatBytes(
-                                        stats.meta.checked_div(stats.meta_count).unwrap_or(0)
-                                    ),
-                                ),
+                                format!(" {}", stats.format_total()),
+                                format!(" {}", stats.format_data()),
+                                format!(" {} x", stats.data_count),
+                                format!("{}", stats.format_avg_data()),
+                                format!(" {}", stats.format_meta()),
+                                format!(" {} x", stats.meta_count),
+                                format!("{}", stats.format_avg_meta()),
                                 format!(" {}", stats.upper_count),
                                 format!(" {}", stats.collectibles_count),
                                 format!(" {}", stats.aggregated_collectibles_count),

PATCH

echo "Fix applied successfully."
