#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: \"Diagnoses and fixes slow Qdrant indexing and data ingestion. Use w" "skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md" && grep -qF "description: \"Diagnoses and reduces Qdrant memory usage. Use when someone report" "skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md" && grep -qF "description: \"Diagnoses and fixes slow Qdrant search. Use when someone reports '" "skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md b/skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md
@@ -0,0 +1,81 @@
+---
+name: qdrant-indexing-performance-optimization
+description: "Diagnoses and fixes slow Qdrant indexing and data ingestion. Use when someone reports 'uploads are slow', 'indexing takes forever', 'optimizer is stuck', 'HNSW build time too long', or 'data uploaded but search is bad'. Also use when optimizer status shows errors, segments won't merge, or indexing threshold questions arise."
+---
+
+# What to Do When Qdrant Indexing Is Too Slow
+
+Qdrant does NOT build HNSW indexes immediately. Small segments use brute-force until they exceed `indexing_threshold_kb` (default: 20 MB). Search during this window is slower by design, not a bug.
+
+- Understand the indexing optimizer [Indexing optimizer](https://qdrant.tech/documentation/concepts/optimizer/#indexing-optimizer)
+
+
+## Uploads/Ingestion Too Slow
+
+Use when: upload or upsert API calls are slow.
+Identify bottleneck: client-side (network, batching) vs server-side (CPU, disk I/O)
+
+For client-side, optimize batching and parallelism:
+
+- Use batch upserts (64-256 points per request) [Points API](https://qdrant.tech/documentation/concepts/points/#upload-points)
+- Use 2-4 parallel upload streams
+
+For server-side, optimize Qdrant configuration and indexing strategy:
+
+- Create more shards (3-12), each shard has an independent update worker [Sharding](https://qdrant.tech/documentation/guides/distributed_deployment/#sharding)
+- Create payload indexes before HNSW builds (needed for filterable vector index) [Payload index](https://qdrant.tech/documentation/concepts/indexing/#payload-index)
+
+Suitable for initial bulk load of large datasets:
+
+- Disable HNSW during bulk load (set `indexing_threshold_kb` very high, restore after) [Collection params](https://qdrant.tech/documentation/concepts/collections/#update-collection-parameters)
+- Setting `m=0` to disable HNSW is legacy, use high `indexing_threshold_kb` instead
+
+Careful, fast unindexed upload might temporarily use more RAM and degrade search performance until optimizer catches up.
+
+See https://qdrant.tech/documentation/tutorials-develop/bulk-upload/
+
+
+## Optimizer Stuck or Taking Too Long
+
+Use when: optimizer running for hours, not finishing.
+
+- Check actual progress via optimizations endpoint (v1.17+) [Optimization monitoring](https://qdrant.tech/documentation/concepts/optimizer/#optimization-monitoring)
+- Large merges and HNSW rebuilds legitimately take hours on big datasets
+- Check CPU and disk I/O (HNSW is CPU-bound, merging is I/O-bound, HDD is not viable)
+- If `optimizer_status` shows an error, check logs for disk full or corrupted segments
+
+
+## HNSW Build Time Too High
+
+Use when: HNSW index build dominates total indexing time.
+
+- Reduce `m` (default 16, good for most cases, 32+ rarely needed) [HNSW params](https://qdrant.tech/documentation/concepts/indexing/#vector-index)
+- Reduce `ef_construct` (100-200 sufficient) [HNSW config](https://qdrant.tech/documentation/concepts/collections/#indexing-vectors-in-hnsw)
+- Keep `max_indexing_threads` proportional to CPU cores [Configuration](https://qdrant.tech/documentation/guides/configuration/)
+- Use GPU for indexing [GPU indexing](https://qdrant.tech/documentation/guides/running-with-gpu/)
+
+## HNSW index for multi-tenant collections
+
+If you have a multi-tenant use-case, where all data is split by some payload field (e.g. `tenant_id`), you can avoid building global HNSW index and instead rely on `payload_m` value to only build HNSW index for subsets of data.
+Skipping global HNSW index can significantly reduce indexing time.
+
+See [Multi-tenant collections](https://qdrant.tech/documentation/guides/multitenancy/) for details.
+
+## Additional payload indexes is too slow
+
+Qdrant builds extra HNSW links for all payload indexes to ensure that quality of filtered vector search does not degrade.
+Some payload indexes (e.g. `text` type with long texts) can have very high number or 
+unique values per point, which can lead to long HNSW build time.
+
+You can disable building extra HNSW links for specific payload index and instead rely on slightly slower query-time strategies like ACORN.
+
+Read more about disabling extra HNSW links in [documentation](https://qdrant.tech/documentation/concepts/indexing/#disable-the-creation-of-extra-edges-for-payload-fields)
+
+Read more about ACORN in [documentation](https://qdrant.tech/documentation/concepts/search/#acorn-search-algorithm)
+
+
+## What NOT to Do
+
+- Do not create payload indexes AFTER HNSW is built (breaks filterable vector index)
+- Do not use `m=0` for bulk uploads into existing collection, it might drop existing HNSW and cause long reindexing 
+- Do not upload one point at a time (per-request overhead dominates)
diff --git a/skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md b/skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md
@@ -0,0 +1,67 @@
+---
+name: qdrant-memory-usage-optimization
+description: "Diagnoses and reduces Qdrant memory usage. Use when someone reports 'memory too high', 'RAM keeps growing', 'node crashed', 'out of memory', 'memory leak', or asks 'why is memory usage so high?', 'how to reduce RAM?'. Also use when memory doesn't match calculations, quantization didn't help, or nodes crash during recovery."
+---
+
+# Understanding memory usage
+
+Qdrant operates with 2 types of RAM memory: 
+
+- Resident memory (aka RSSAnon) - memory used for internal data structures like ID tracker, and some components forced to stay in RAM, quantized vectors if `always_ram=true`, payload indexes, e.t.c.
+
+- OS page cache - memory used for caching disk reads, which can be released when needed. Original vectors are normally stored in page cahce, so the service won't crash if RAM is full, but performance may degrade.
+
+It is normal of OS page cache to occupy whole available RAM, but if resident memory is above 80% of total, it's a sign of a problem.
+
+## Memory usage monitoring
+
+- Qdrant exposes memory usage with `/metrics` endpoint see more in [Monitoring docs](https://qdrant.tech/documentation/guides/monitoring/).
+
+<!-- ToDo: Talk about memory usage of each components once API is available -->
+
+
+## How much memory is needed for Qdrant?
+
+Optimal memory usage depends on the use case.
+
+- For regular search scenarios general guidelines are provided in [Capacity planning docs](https://qdrant.tech/documentation/guides/capacity-planning/).
+
+For detailed breakdown of memory usage on a large scale exmaple see [Large scale memory usage example](https://qdrant.tech/documentation/tutorials-operations/large-scale-search/#memory-usage).
+
+Payload indexes and HNSW graph also require memory, along with vectors themselves, so it's important to consider them in calculations.
+
+Additionally, qdrant requires some extra memory for optimizations. During optimization, optimized segments are fully loaded into RAM, so it is importat to have some headroom for that.
+Large the `max_segment_size`, more headroom is needed.
+
+
+### When to put HNSW index on disk
+
+Putting frequently used components (such as HNSW index) on disk might cause significant performance degradation.
+There are some scenarios, however, when it can be a good option:
+
+- Deployments with low latency disks - local NVMe or similar.
+- Multi-tenant deployments, where only a subset of tenants is frequently accessed, so that only a fraction of data & index is loaded in RAM at a time.
+- For deployments with [inline storage](https://qdrant.tech/documentation/guides/optimize/#inline-storage-in-hnsw-index) enabled.
+
+
+## How to minimize memory footprint
+
+The main challenge is to put on disk those parts of data, which are rarely accessed.
+Here are the main techniques to achieve that:
+
+- Use quantization to store only compressed vectors in ram [Quantization docs](https://qdrant.tech/documentation/guides/quantization/)
+
+- Use float16 or int8 datatypes to reduce memory usage of vectors by 2x or 4x respectively, with some tradeoff in precision. Read more about vector datatypes in [documentation](https://qdrant.tech/documentation/concepts/vectors/#datatypes)
+
+- Leverage Matryoshka Representation Learning (MRL) to store only small vectors in RAM, while keeping large vectors on disk. Examples of how to use MRL with qdrant cloud inferece: [MRL docs](https://qdrant.tech/documentation/concepts/inference/#reduce-vector-dimensionality-with-matryoshka-models)
+
+- For multi-tenant deployments with small tenants, vectors might be stored on-disk, as same tenant data is stored together [Multitenancy docs](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-performance)
+
+- For deployments with fast local storage and relatively low requirements for search throughput, it may be possible to store all components of vector store on disk. Read more about the performance implications of on-disk storage in [the article](https://qdrant.tech/articles/memory-consumption/)
+
+- For low RAM environments, consider `async_scorer` config, which enables support of `io_uring` for parallel disk access, which can significantly improve performance of on-disk storage. Read more about `async_scorer` in [the article](https://qdrant.tech/articles/io_uring/) (only available on Linux with kernel 5.11+)
+
+- Consider storing Sparse Vectors and text payload on disk, as they are usually more disk-friently compared to dense vectors. 
+    - Configuring payload indexes to be stored on disk [docs](https://qdrant.tech/documentation/concepts/indexing/#on-disk-payload-index)
+    - Configuring sparse vectors to be stored on disk [docs](https://qdrant.tech/documentation/concepts/indexing/#sparse-vector-index)
+
diff --git a/skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md b/skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md
@@ -0,0 +1,60 @@
+---
+name: qdrant-search-speed-optimization
+description: "Diagnoses and fixes slow Qdrant search. Use when someone reports 'search is slow', 'high latency', 'queries take too long', 'low QPS', 'throughput too low', 'filtered search is slow', or 'search was fast but now it's slow'. Also use when search performance degrades after config changes or data growth."
+---
+
+# What to Do When Qdrant Search Is Too Slow
+
+First determine whether the problem is latency (single query speed) or throughput (queries per second). These pull in opposite directions. Getting this wrong means tuning the wrong knob.
+
+- Understand the tradeoff [Latency vs throughput](https://qdrant.tech/documentation/guides/optimize/#balancing-latency-and-throughput)
+
+
+## Single Query Too Slow (Latency)
+
+Use when: individual queries take too long regardless of load.
+
+- Reduce `hnsw_ef` at query time (64-128 is usually sufficient) [Fine-tuning search](https://qdrant.tech/documentation/guides/optimize/#fine-tuning-search-parameters)
+- Enable scalar int8 quantization with `always_ram=true` [Scalar quantization](https://qdrant.tech/documentation/guides/quantization/#scalar-quantization)
+- Enable io_uring for disk-heavy workloads on Linux [io_uring](https://qdrant.tech/articles/io_uring/)
+- Check for unmerged segments after uploads [Merge optimizer](https://qdrant.tech/documentation/concepts/optimizer/#merge-optimizer)
+- Use oversampling + rescore for high-dimensional vectors [Search with quantization](https://qdrant.tech/documentation/guides/quantization/#searching-with-quantization)
+
+
+## Can't Handle Enough QPS (Throughput)
+
+Use when: system can't serve enough queries per second under load.
+
+- Reduce segment count (`default_segment_number` to 2) [Maximizing throughput](https://qdrant.tech/documentation/guides/optimize/#maximizing-throughput)
+- Use batch search API instead of single queries [Batch search](https://qdrant.tech/documentation/concepts/search/#batch-search-api)
+- Enable quantization to reduce CPU cost [Scalar quantization](https://qdrant.tech/documentation/guides/quantization/#scalar-quantization)
+- Add replicas to distribute read load [Replication](https://qdrant.tech/documentation/guides/distributed_deployment/#replication)
+
+
+## Filtered Search Is Slow
+
+Use when: filtered search is significantly slower than unfiltered. Most common SA complaint after memory.
+
+- Create payload index on the filtered field [Payload index](https://qdrant.tech/documentation/concepts/indexing/#payload-index)
+- Use `is_tenant=true` for high-cardinality tenant fields [Tenant index](https://qdrant.tech/documentation/concepts/indexing/#tenant-index)
+- Try ACORN algorithm for very restrictive filters (v1.13+) [Filterable HNSW](https://qdrant.tech/documentation/concepts/indexing/#filterable-hnsw-index)
+- If payload index was added after HNSW build, trigger re-index to create filterable subgraph links
+
+
+## Search Was Fast, Now It's Slow
+
+Use when: search performance degraded without obvious config changes. Classic pattern after bulk uploads.
+
+- Check optimizer status (most likely still running after upload) [Optimizer monitoring](https://qdrant.tech/documentation/concepts/optimizer/#optimization-monitoring)
+- Check segment count (unmerged segments from bulk upload) [Merge optimizer](https://qdrant.tech/documentation/concepts/optimizer/#merge-optimizer)
+- Check for cache eviction from competing processes
+- Do NOT make config changes while the optimizer is running
+
+
+## What NOT to Do
+
+- Set `always_ram=false` on quantization (disk thrashing on every search)
+- Put HNSW on disk for latency-sensitive production (only for cold storage)
+- Increase segment count for throughput (opposite: fewer = better)
+- Create payload indexes on every field (wastes memory)
+- Blame Qdrant before checking optimizer status
PATCH

echo "Gold patch applied."
