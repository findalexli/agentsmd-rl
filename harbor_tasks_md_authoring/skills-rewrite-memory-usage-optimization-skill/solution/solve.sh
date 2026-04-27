#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "Qdrant uses two types of RAM: resident memory (RSSAnon) for data structures, qua" "skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md b/skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md
@@ -3,65 +3,53 @@ name: qdrant-memory-usage-optimization
 description: "Diagnoses and reduces Qdrant memory usage. Use when someone reports 'memory too high', 'RAM keeps growing', 'node crashed', 'out of memory', 'memory leak', or asks 'why is memory usage so high?', 'how to reduce RAM?'. Also use when memory doesn't match calculations, quantization didn't help, or nodes crash during recovery."
 ---
 
-# Understanding memory usage
+# What to Do When Qdrant Uses Too Much Memory
 
-Qdrant operates with 2 types of RAM memory: 
+Qdrant uses two types of RAM: resident memory (RSSAnon) for data structures, quantized vectors, payload indexes, and OS page cache for caching disk reads. Page cache filling all available RAM is normal. If resident memory exceeds 80% of total RAM, investigate.
 
-- Resident memory (aka RSSAnon) - memory used for internal data structures like ID tracker, and some components forced to stay in RAM, quantized vectors if `always_ram=true`, payload indexes, e.t.c.
+- Understand memory breakdown [Memory article](https://qdrant.tech/articles/memory-consumption/)
 
-- OS page cache - memory used for caching disk reads, which can be released when needed. Original vectors are normally stored in page cahce, so the service won't crash if RAM is full, but performance may degrade.
 
-It is normal of OS page cache to occupy whole available RAM, but if resident memory is above 80% of total, it's a sign of a problem.
+## Don't Know What's Using Memory
 
-## Memory usage monitoring
+Use when: memory is higher than expected and you need to find the cause.
 
-- Qdrant exposes memory usage with `/metrics` endpoint see more in [Monitoring docs](https://qdrant.tech/documentation/guides/monitoring/).
+- Check `/metrics` for process-level memory (RSS, allocated bytes, page faults) [Monitoring docs](https://qdrant.tech/documentation/guides/monitoring/)
+- Use `/telemetry` for per-segment breakdown: `ram_usage_bytes`, `vectors_size_bytes`, `payloads_size_bytes` per segment
+- Estimate expected memory: `num_vectors * dimensions * 4 bytes * 1.5` plus payload and index overhead [Capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/)
+- For large scale reference [Large scale memory example](https://qdrant.tech/documentation/tutorials-operations/large-scale-search/#memory-usage)
+- Common causes of unexpected growth: quantized vectors with `always_ram=true`, too many payload indexes, large `max_segment_size` during optimization
 
-<!-- ToDo: Talk about memory usage of each components once API is available -->
 
+## Memory Too High for Dataset Size
 
-## How much memory is needed for Qdrant?
+Use when: resident memory exceeds what the dataset should need.
 
-Optimal memory usage depends on the use case.
+- Use quantization to store compressed vectors in RAM [Quantization](https://qdrant.tech/documentation/guides/quantization/)
+- Use float16 or uint8 datatypes to reduce vector memory by 2x or 4x [Datatypes](https://qdrant.tech/documentation/concepts/vectors/#datatypes)
+- Use Matryoshka models to store smaller vectors in RAM, larger on disk [MRL](https://qdrant.tech/documentation/concepts/inference/#reduce-vector-dimensionality-with-matryoshka-models)
+- Move payload indexes to disk if filtering is infrequent [On-disk payload index](https://qdrant.tech/documentation/concepts/indexing/#on-disk-payload-index)
+- Move sparse vectors to disk [Sparse vector index](https://qdrant.tech/documentation/concepts/indexing/#sparse-vector-index)
 
-- For regular search scenarios general guidelines are provided in [Capacity planning docs](https://qdrant.tech/documentation/guides/capacity-planning/).
+Payload indexes and HNSW graph also consume memory. Include them in calculations. During optimization, segments are fully loaded into RAM. Larger `max_segment_size` means more headroom needed.
 
-For detailed breakdown of memory usage on a large scale exmaple see [Large scale memory usage example](https://qdrant.tech/documentation/tutorials-operations/large-scale-search/#memory-usage).
 
-Payload indexes and HNSW graph also require memory, along with vectors themselves, so it's important to consider them in calculations.
+## Want Everything on Disk
 
-Additionally, qdrant requires some extra memory for optimizations. During optimization, optimized segments are fully loaded into RAM, so it is importat to have some headroom for that.
-Large the `max_segment_size`, more headroom is needed.
+Use when: RAM budget is very tight and you accept slower search.
 
+- Store all vector components on disk with mmap [On-disk storage](https://qdrant.tech/articles/memory-consumption/)
+- For multi-tenant deployments with small tenants, on-disk works well since same-tenant data is co-located [Multitenancy](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-performance)
+- Enable `async_scorer` with `io_uring` for parallel disk access on Linux (kernel 5.11+) [io_uring](https://qdrant.tech/articles/io_uring/)
+- Consider inline HNSW storage [Inline storage](https://qdrant.tech/documentation/guides/optimize/#inline-storage-in-hnsw-index)
 
-### When to put HNSW index on disk
+HNSW on disk causes significant performance degradation except: local NVMe, multi-tenant with partial access patterns, or inline storage enabled.
 
-Putting frequently used components (such as HNSW index) on disk might cause significant performance degradation.
-There are some scenarios, however, when it can be a good option:
 
-- Deployments with low latency disks - local NVMe or similar.
-- Multi-tenant deployments, where only a subset of tenants is frequently accessed, so that only a fraction of data & index is loaded in RAM at a time.
-- For deployments with [inline storage](https://qdrant.tech/documentation/guides/optimize/#inline-storage-in-hnsw-index) enabled.
-
-
-## How to minimize memory footprint
-
-The main challenge is to put on disk those parts of data, which are rarely accessed.
-Here are the main techniques to achieve that:
-
-- Use quantization to store only compressed vectors in ram [Quantization docs](https://qdrant.tech/documentation/guides/quantization/)
-
-- Use float16 or int8 datatypes to reduce memory usage of vectors by 2x or 4x respectively, with some tradeoff in precision. Read more about vector datatypes in [documentation](https://qdrant.tech/documentation/concepts/vectors/#datatypes)
-
-- Leverage Matryoshka Representation Learning (MRL) to store only small vectors in RAM, while keeping large vectors on disk. Examples of how to use MRL with qdrant cloud inferece: [MRL docs](https://qdrant.tech/documentation/concepts/inference/#reduce-vector-dimensionality-with-matryoshka-models)
-
-- For multi-tenant deployments with small tenants, vectors might be stored on-disk, as same tenant data is stored together [Multitenancy docs](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-performance)
-
-- For deployments with fast local storage and relatively low requirements for search throughput, it may be possible to store all components of vector store on disk. Read more about the performance implications of on-disk storage in [the article](https://qdrant.tech/articles/memory-consumption/)
-
-- For low RAM environments, consider `async_scorer` config, which enables support of `io_uring` for parallel disk access, which can significantly improve performance of on-disk storage. Read more about `async_scorer` in [the article](https://qdrant.tech/articles/io_uring/) (only available on Linux with kernel 5.11+)
-
-- Consider storing Sparse Vectors and text payload on disk, as they are usually more disk-friently compared to dense vectors. 
-    - Configuring payload indexes to be stored on disk [docs](https://qdrant.tech/documentation/concepts/indexing/#on-disk-payload-index)
-    - Configuring sparse vectors to be stored on disk [docs](https://qdrant.tech/documentation/concepts/indexing/#sparse-vector-index)
+## What NOT to Do
 
+- Assume memory leak when page cache fills RAM (normal OS behavior)
+- Put HNSW on disk for latency-sensitive production without NVMe
+- Ignore `max_segment_size` headroom during optimization (causes temporary OOM)
+- Run at >90% resident memory (cache eviction causes severe performance degradation)
+- Create payload indexes on every field (each index consumes memory)
PATCH

echo "Gold patch applied."
