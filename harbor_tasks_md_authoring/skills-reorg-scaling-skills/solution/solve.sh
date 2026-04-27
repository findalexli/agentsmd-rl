#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "Vertical scaling, horizontal scaling, throughput, latency, IOPS, and memory pres" "skills/qdrant-scaling/SKILL.md" && grep -qF "**Start vertical, go horizontal only when you must.** Horizontal scaling adds pe" "skills/qdrant-scaling/performance-scaling/SKILL.md" && grep -qF "skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md" "skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md" && grep -qF "description: \"Guides Qdrant vertical scaling decisions. Use when someone asks 'h" "skills/qdrant-scaling/performance-scaling/vertical-scaling/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-scaling/SKILL.md b/skills/qdrant-scaling/SKILL.md
@@ -14,16 +14,12 @@ First determine what you're scaling for: data volume, query throughput (QPS), qu
 - Understand the tradeoff [Latency vs throughput](https://qdrant.tech/documentation/guides/optimize/#balancing-latency-and-throughput)
 - High speed vs high precision vs low memory: [qdrant performance](https://qdrant.tech/documentation/operations/optimize/)
 
-## Horizontal Scaling
 
-Sharding, resharding, shard planning, vertical vs horizontal decision, and prerequisites for zero-downtime scaling. [Horizontal Scaling](horizontal-scaling/SKILL.md)
+## Performance & Capacity Scaling
 
-
-## Performance Scaling
-
-Throughput (queries per second, QPS), latency, IOPS limitations, and memory pressure. Different dimensions that pull in different directions. [Performance Scaling](performance-scaling/SKILL.md)
+Vertical scaling, horizontal scaling, throughput, latency, IOPS, and memory pressure. Start vertical, go horizontal only when necessary -- horizontal scaling is effectively a one-way street. [Performance Scaling](performance-scaling/SKILL.md)
 
 
 ## Tenant Scaling
 
-Multi-tenant workloads with payload partitioning, per-tenant indexes, and tiered multitenancy. [Tenant Scaling](tenant-scaling/SKILL.md)
+Multi-tenant workloads with payload partitioning, per-tenant indexes, and tiered multitenancy. [Tenant Scaling](tenant-scaling/SKILL.md)
\ No newline at end of file
diff --git a/skills/qdrant-scaling/performance-scaling/SKILL.md b/skills/qdrant-scaling/performance-scaling/SKILL.md
@@ -1,67 +1,75 @@
 ---
 name: qdrant-performance-scaling
-description: "Diagnoses and guides Qdrant performance scaling for throughput, latency, IOPS, and memory pressure. Use when someone reports 'need more throughput', 'need lower latency', 'queries timeout', 'IOPS saturated', 'memory too high after scaling', or 'read latency 10x during ingestion'. Also use when performance degrades after scaling or config changes."
+description: "Guides Qdrant scaling decisions for capacity and performance. Use when someone asks about vertical vs horizontal scaling, node sizing, throughput, latency, IOPS, memory pressure, 'how to scale Qdrant', 'need more capacity', or when performance degrades. Routes to vertical scaling, horizontal scaling, or performance tuning as appropriate."
 ---
 
-# What to Do When Qdrant Performance Needs to Scale
+# Scaling Qdrant for Performance and Capacity
 
-Scaling for throughput and latency are opposite tuning directions. Fewer segments = better throughput. More segments = better latency. Cannot optimize both on the same node.
+Scaling Qdrant means either scaling **up** (vertical -- bigger nodes) or scaling **out** (horizontal -- more nodes). The right choice depends on what you're scaling for and where you are in your growth trajectory.
 
-- Understand the tradeoff [Latency vs throughput](https://qdrant.tech/documentation/guides/optimize/#balancing-latency-and-throughput)
+**Start vertical, go horizontal only when you must.** Horizontal scaling adds permanent operational complexity -- sharding, replication, rebalancing, network overhead -- and is effectively a one-way street. Once you distribute data across nodes, consolidating back to fewer nodes is difficult and risky. Vertical scaling is simpler, reversible, and sufficient for most workloads up to ~100M vectors per node.
 
 
-## Scaling for Higher RPS
+## Scaling Dimensions
 
-Use when: system can't serve enough queries per second under load.
+Different scaling needs pull in different directions. Identify your primary constraint before choosing a strategy.
+
+- **Data volume:** How much data needs to fit? RAM, disk, and quantization are the levers. Start with vertical (bigger nodes, quantization, mmap). Go horizontal only when a single node can't hold the data or when you need fault tolerance/isolation.
+- **Query throughput (QPS):** How many queries per second? Fewer segments, quantization with `always_ram=true`, and batch APIs help. Read replicas scale this horizontally.
+- **Query latency:** How fast must individual queries respond? More segments (matching CPU cores), in-RAM quantized vectors, and lower `hnsw_ef`. Throughput and latency are opposite tuning directions -- you cannot optimize both on the same node.
+- **Tenant count:** How many tenants share the cluster? Use payload partitioning with `is_tenant=true`. See [Tenant Scaling](../tenant-scaling/SKILL.md).
+
+Understand the core tradeoff: [Latency vs throughput](https://qdrant.tech/documentation/guides/optimize/#balancing-latency-and-throughput)
+
+
+## Performance Tuning (Independent of Scaling Direction)
+
+These optimizations apply regardless of whether you scale vertically or horizontally.
+
+### For Higher RPS
 
 - Use fewer, larger segments (`default_segment_number: 2`) [Maximizing throughput](https://qdrant.tech/documentation/guides/optimize/#maximizing-throughput)
 - Enable quantization with `always_ram=true` to reduce CPU per query [Quantization](https://qdrant.tech/documentation/guides/quantization/)
-- Add read replicas to distribute query load [Replication](https://qdrant.tech/documentation/guides/distributed_deployment/#replication)
 - Use batch search API to amortize overhead [Batch search](https://qdrant.tech/documentation/concepts/search/#batch-search-api)
 - Configure update throughput control (v1.17+) to prevent unoptimized searches degrading reads [Low latency search](https://qdrant.tech/documentation/guides/low-latency-search/)
-- Set `optimizer_cpu_budget` to limit indexing CPUs (e.g. `2` on an 8-CPU node reserves 6 for queries, `0` = auto, negative = subtract from available)
-
-
-## Scaling for Lower Latency
+- Set `optimizer_cpu_budget` to limit indexing CPUs (e.g. `2` on an 8-CPU node reserves 6 for queries)
 
-Use when: individual query latency is too high regardless of load.
+### For Lower Latency
 
 - Increase segment count to match CPU cores (`default_segment_number: 16`) [Minimizing latency](https://qdrant.tech/documentation/guides/optimize/#minimizing-latency)
-- Keep quantized vectors and HNSW in RAM (`always_ram=true`) [High precision with speed](https://qdrant.tech/documentation/guides/optimize/#improving-precision)
+- Keep quantized vectors and HNSW in RAM (`always_ram=true`)
 - Reduce `hnsw_ef` at query time (trade recall for speed) [Search params](https://qdrant.tech/documentation/guides/optimize/#fine-tuning-search-parameters)
 - Use local NVMe, avoid network-attached storage
-- Configure delayed read fan-out (v1.17+) for tail latency in distributed clusters [Delayed fan-outs](https://qdrant.tech/documentation/guides/low-latency-search/#use-delayed-fan-outs)
-
-
-## Scaling for Disk I/O (IOPS)
+- Configure delayed read fan-out (v1.17+) for tail latency [Delayed fan-outs](https://qdrant.tech/documentation/guides/low-latency-search/#use-delayed-fan-outs)
 
-Use when: queries timeout despite adequate CPU/RAM, disk throughput saturated. Major production issue.
+### For Disk I/O (IOPS)
 
-Symptoms: IOPS near provider limits, high latency during concurrent reads/writes, page cache thrashing.
-
-- Scale out horizontally: each node adds independent IOPS (6 nodes = 6x IOPS vs 1 node)
-- Upgrade to provisioned IOPS or local NVMe
+- Upgrade to provisioned IOPS or local NVMe first
 - Use `io_uring` on Linux (kernel 5.11+) [io_uring article](https://qdrant.tech/articles/io_uring/)
-- Put sparse vectors and text payloads on disk (less IOPS-intensive)
+- Put sparse vectors and text payloads on disk
 - Set `indexing_threshold` high during bulk ingestion to defer indexing
+- If still saturated, scale out horizontally (each node adds independent IOPS)
 
-
-## Scaling for Memory Pressure
-
-Use when: memory working set >80%, OS cache eviction, OOM errors.
+### For Memory Pressure
 
 - Vertical scale RAM first. Critical if working set >80%.
-- Set `optimizer_cpu_budget` to limit background optimization CPUs
-- Schedule indexing: set high `indexing_threshold` during peak hours
 - Use quantization: scalar (4x reduction) or binary (16x reduction) [Quantization](https://qdrant.tech/documentation/guides/quantization/)
 - Move payload indexes to disk if filtering is infrequent [On-disk payload index](https://qdrant.tech/documentation/concepts/indexing/#on-disk-payload-index)
+- Set `optimizer_cpu_budget` to limit background optimization CPUs
+- Schedule indexing: set high `indexing_threshold` during peak hours
+
+
+## Dedicated Scaling Guides
 
-[Memory optimization](https://qdrant.tech/documentation/guides/optimize/)
+- **[Vertical Scaling](vertical-scaling/SKILL.md)** -- Node sizing, RAM/CPU/disk guidelines, scaling up in Qdrant Cloud, and maximizing single-node capacity before going horizontal.
+- **[Horizontal Scaling](horizontal-scaling/SKILL.md)** -- Sharding, resharding, shard planning, node count decisions, and prerequisites for zero-downtime distributed scaling.
 
 
 ## What NOT to Do
 
+- Do not scale horizontally before exhausting vertical options (adds permanent, irreversible complexity)
 - Do not expect to optimize throughput and latency simultaneously on the same node
-- Do not scale horizontally when IOPS-bound without also increasing disk tier
+- Do not scale horizontally when IOPS-bound without also upgrading disk tier
 - Do not run at >90% RAM (OS cache eviction = severe performance degradation)
-- Do not ignore optimizer status during performance debugging
+- Do not scale down RAM without load testing (cache eviction causes days-long latency incidents)
+- Do not ignore optimizer status during performance debugging
\ No newline at end of file
diff --git a/skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md b/skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md

diff --git a/skills/qdrant-scaling/performance-scaling/vertical-scaling/SKILL.md b/skills/qdrant-scaling/performance-scaling/vertical-scaling/SKILL.md
@@ -0,0 +1,104 @@
+---
+name: qdrant-vertical-scaling
+description: "Guides Qdrant vertical scaling decisions. Use when someone asks 'how to scale up a node', 'need more RAM', 'upgrade node size', 'vertical scaling', 'resize cluster', 'scale up vs scale out', or when memory/CPU is insufficient on current nodes. Also use when someone wants to avoid the complexity of horizontal scaling."
+---
+
+# What to Do When Qdrant Needs to Scale Vertically
+
+Vertical scaling means increasing CPU, RAM, or disk on existing nodes rather than adding more nodes. This is the recommended first step before considering horizontal scaling. Vertical scaling is simpler, avoids distributed system complexity, and is reversible.
+
+- Vertical scaling for Qdrant Cloud is done through the [Qdrant Cloud Console](https://cloud.qdrant.io/)
+- For self-hosted deployments, resize the underlying VM or container resources
+- Get a snapshot of the cluster information: 
+```bash
+curl http://localhost:6333/collections/collection_name/cluster \
+     -H "api-key: <apiKey>"
+```
+
+## When to Scale Vertically
+
+Use when: current node resources (RAM, CPU, disk) are insufficient, but the workload doesn't yet require distribution.
+
+- RAM usage approaching 80% of available memory (OS page cache eviction starts, severe performance degradation)
+- CPU saturation during query serving or indexing
+- Disk space running low for on-disk vectors, payloads, or WAL
+- A single node can handle up to ~100M vectors depending on dimensions and quantization
+- You want to avoid the operational complexity of sharding and replication
+
+
+## How to Scale Vertically in Qdrant Cloud
+
+Vertical scaling is managed through the Qdrant Cloud Console. You cannot resize nodes via API (not yet, but planned for future release!!!)
+
+- Log into [Qdrant Cloud Console](https://cloud.qdrant.io/)
+- Select the cluster to resize
+- Choose a larger node configuration (more RAM, CPU, or both)
+- The upgrade process involves a rolling restart with minimal downtime if replication is configured
+- Ensure `replication_factor: 2` or higher before resizing to maintain availability during the rolling restart
+
+**Important:** Scaling up is straightforward. Scaling down requires care -- if the working set no longer fits in RAM after downsizing, performance will degrade severely due to cache eviction. Always load test before scaling down.
+
+
+## RAM Sizing Guidelines
+
+RAM is the most critical resource for Qdrant performance. Use these guidelines to right-size.
+
+- Base formula: `num_vectors * dimensions * 4 bytes * 1.5` for full-precision vectors in RAM
+- With scalar quantization: divide by 4 (INT8 reduces each float32 to 1 byte) [Quantization](https://qdrant.tech/documentation/guides/quantization/)
+- With binary quantization: divide by 32 [Binary quantization](https://qdrant.tech/documentation/guides/quantization/#binary-quantization)
+- Add overhead for HNSW index (~20-30% of vector data), payload indexes, and WAL
+- Reserve 20% headroom for optimizer operations and OS cache
+- Monitor actual usage via Grafana/Prometheus before and after resizing [Monitoring](https://qdrant.tech/documentation/guides/monitoring/)
+
+
+## CPU Sizing Guidelines
+
+CPU needs depend on query patterns and indexing load.
+
+- More CPU cores = more parallel segment searches = lower latency
+- Set `default_segment_number` to match available CPU cores for latency-optimized workloads [Minimizing latency](https://qdrant.tech/documentation/guides/optimize/#minimizing-latency)
+- Use `optimizer_cpu_budget` to control how many cores are reserved for indexing vs queries
+- Heavy write workloads (continuous ingestion) benefit from more cores to keep up with optimization
+
+
+## Disk Sizing Guidelines
+
+Disk matters most when using mmap or on-disk storage.
+
+- mmap storage: vectors live on disk with RAM as page cache. Size disk to hold full vector data + 2x for optimization headroom [On-disk storage](https://qdrant.tech/documentation/guides/capacity-planning/#choosing-disk-over-ram)
+- Use NVMe/SSD, never HDD. Local NVMe preferred over network-attached for latency-sensitive workloads
+- WAL (Write-Ahead Log) needs disk space proportional to write throughput
+- On-disk payload indexes need additional space if payloads are large
+
+
+## Maximizing a Single Node Before Going Horizontal
+
+Before adding nodes, exhaust these vertical optimization strategies:
+
+- Enable quantization to reduce memory footprint 4-32x [Quantization](https://qdrant.tech/documentation/guides/quantization/)
+- Use mmap to move vectors to disk, keeping hot data in RAM cache [Capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/)
+- Move infrequently filtered payload indexes to disk [On-disk payload index](https://qdrant.tech/documentation/concepts/indexing/#on-disk-payload-index)
+- Tune HNSW parameters (`m`, `ef_construct`) to trade recall for memory [HNSW configuration](https://qdrant.tech/documentation/concepts/indexing/#vector-index)
+- Use `optimizer_cpu_budget` to balance indexing and query CPU usage
+
+
+## When Vertical Scaling Is No Longer Enough
+
+Recognize these signals that it's time to go horizontal:
+
+- Data volume exceeds what a single node can hold even with quantization and mmap
+- IOPS are saturated (more nodes = more independent disk I/O)
+- Need fault tolerance (requires replication across nodes)
+- Need tenant isolation via dedicated shards
+- Single-node CPU is maxed and query latency is unacceptable
+
+When you hit these limits, see [Horizontal Scaling](../horizontal-scaling/SKILL.md) for guidance on sharding and node planning.
+
+
+## What NOT to Do
+
+- Do not scale down RAM without load testing first (cache eviction = severe latency degradation that can last days)
+- Do not ignore the 80% RAM threshold (performance cliff, not gradual degradation)
+- Do not skip replication before resizing in Cloud (rolling restart without replicas = downtime)
+- Do not jump to horizontal scaling before exhausting vertical options (adds permanent operational complexity)
+- Do not assume more CPU always helps (IOPS-bound workloads won't improve with more cores)
\ No newline at end of file
PATCH

echo "Gold patch applied."
