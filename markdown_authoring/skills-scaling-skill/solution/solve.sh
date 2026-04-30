#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: \"Guides Qdrant scaling decisions. Use when someone asks 'how many n" "skills/qdrant-scaling/SKILL.md" && grep -qF "description: \"Diagnoses and guides Qdrant horizontal scaling decisions. Use when" "skills/qdrant-scaling/horizontal-scaling/SKILL.md" && grep -qF "description: \"Diagnoses and guides Qdrant performance scaling for throughput, la" "skills/qdrant-scaling/performance-scaling/SKILL.md" && grep -qF "description: \"Guides Qdrant multi-tenant scaling. Use when someone asks 'how to " "skills/qdrant-scaling/tenant-scaling/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-scaling/SKILL.md b/skills/qdrant-scaling/SKILL.md
@@ -1,44 +1,29 @@
 ---
 name: qdrant-scaling
-description: "How to handle scaling of Qdrant, including horizontal and vertical scaling strategies, sharding, replication, and load balancing. Use when you want to scale your Qdrant deployment to handle increased load or larger datasets."
+description: "Guides Qdrant scaling decisions. Use when someone asks 'how many nodes do I need', 'data doesn't fit on one node', 'need more throughput', 'cluster is slow', 'too many tenants', 'vertical or horizontal', 'how to shard', or 'need to add capacity'."
 allowed-tools:
   - Read
   - Grep
   - Glob
 ---
 
-
 # Qdrant Scaling
 
-Qdrant is designed to handle both large datasets and high query loads, and provides different scaling options to meet the needs of different use cases.
-This document navigates through different scenarios of scaling Qdrant, required in different use cases.
-
-
-## Scaling for larger data volume
-
-<!-- ToDo -->
-
-## Vertical vs Horizontal Scaling
-
-<!-- ToDO -->
-
-### Resharding
-
-<!-- ToDO -->
+First determine what you're scaling for: data volume, query throughput (QPS), query latency, tenant count, or IOPS. Each pulls toward different strategies. Scaling for throughput and latency are opposite tuning directions.
 
-## Scaling for higher RPS
+- Understand the tradeoff [Latency vs throughput](https://qdrant.tech/documentation/guides/optimize/#balancing-latency-and-throughput)
+- High speed vs high precision vs low memory: [qdrant performance](https://qdrant.tech/documentation/operations/optimize/)
 
-<!-- ToDO -->
+## Horizontal Scaling
 
-## Scaling for lower latency
+Sharding, resharding, shard planning, vertical vs horizontal decision, and prerequisites for zero-downtime scaling. [Horizontal Scaling](horizontal-scaling/SKILL.md)
 
 
-<!-- ToDO -->
+## Performance Scaling
 
-## Scaling tenants
+Throughput (queries per second, QPS), latency, IOPS limitations, and memory pressure. Different dimensions that pull in different directions. [Performance Scaling](performance-scaling/SKILL.md)
 
-<!-- ToDO -->
 
-## Scaling for time window rotation
+## Tenant Scaling
 
-<!-- ToDO -->
\ No newline at end of file
+Multi-tenant workloads with payload partitioning, per-tenant indexes, and tiered multitenancy. [Tenant Scaling](tenant-scaling/SKILL.md)
diff --git a/skills/qdrant-scaling/horizontal-scaling/SKILL.md b/skills/qdrant-scaling/horizontal-scaling/SKILL.md
@@ -0,0 +1,64 @@
+---
+name: qdrant-horizontal-scaling
+description: "Diagnoses and guides Qdrant horizontal scaling decisions. Use when someone asks 'vertical or horizontal?', 'how many nodes?', 'how many shards?', 'how to add nodes', 'resharding', 'data doesn't fit', or 'need more capacity'. Also use when data growth outpaces current deployment."
+---
+
+# What to Do When Qdrant Needs More Capacity
+
+Vertical first: simpler operations, no network overhead, good up to ~100M vectors per node depending on dimensions and quantization. Horizontal when: data exceeds single node capacity, need fault tolerance, need to isolate tenants, or IOPS-bound (more nodes = more independent IOPS).
+
+- Estimate memory needs: `num_vectors * dimensions * 4 bytes * 1.5` plus payload and index overhead. Reserve 20% headroom for optimizations. [Capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/)
+
+
+## Not Ready to Scale Yet
+
+Use when: planning to scale but haven't started. Cover these prerequisites before proceeding.
+
+- Minimum 3 nodes with `replication_factor: 2` for zero-downtime scaling
+- Set up monitoring (Grafana/Prometheus) BEFORE scaling
+
+See [Prerequisites](https://qdrant.tech/documentation/guides/distributed_deployment/#enabling-distributed-mode-in-self-hosted-qdrant)
+
+
+## Data Doesn't Fit on One Node
+
+Use when: approaching memory or disk limits on a single node.
+
+- Use quantization to reduce vector memory by 4x (scalar) or 32x (binary) [Quantization](https://qdrant.tech/documentation/guides/quantization/)
+- Use mmap storage to keep vectors on disk with RAM as cache [Choosing disk over RAM](https://qdrant.tech/documentation/guides/capacity-planning/#choosing-disk-over-ram)
+- If still not enough, add nodes with sharding [Sharding](https://qdrant.tech/documentation/guides/distributed_deployment/#sharding)
+
+Most people jump to horizontal too early. Exhaust vertical options first.
+
+
+## Need to Change Shard Count
+
+Use when: shard count isn't evenly divisible by node count, causing uneven distribution, or need to rebalance.
+
+Resharding is expensive and time-consuming. Hours to weeks depending on data size. Locks segments during transfer, queries may timeout under high concurrency.
+
+- Available in Qdrant Cloud (v1.13+) [Resharding](https://qdrant.tech/documentation/guides/distributed_deployment/#resharding)
+- For self-hosted, requires recreating the collection with the new shard count
+- Move shards between nodes to rebalance load [Moving shards](https://qdrant.tech/documentation/guides/distributed_deployment/#moving-shards)
+- List existing shard keys via API (v1.17+) [User-defined sharding](https://qdrant.tech/documentation/guides/distributed_deployment/#user-defined-sharding)
+
+Better alternatives: over-provision shards initially, or spin up new cluster with correct config and migrate data.
+
+
+## Planning for Future Growth
+
+Use when: setting up a new cluster and want to avoid resharding later.
+
+- Estimate data growth to 2-3 year projection
+- Choose LCM shard count: 48 shards works for 12, 16, or 24 nodes. 24 shards works for 6, 8, 12, or 24 nodes.
+- `shard_number` should be 1-2x current node count (allows 2x growth)
+
+
+## What NOT to Do
+
+- Do not jump to horizontal before exhausting vertical (adds complexity for no gain)
+- Do not set `shard_number` that isn't a multiple of node count (uneven distribution)
+- Do not use `replication_factor: 1` in production if you need fault tolerance
+- Do not add nodes without rebalancing shards (use shard move API to redistribute)
+- Do not scale down RAM without load testing (cache eviction causes days-long latency incidents)
+- Do not hit the collection limit by using one collection per tenant (use payload partitioning)
diff --git a/skills/qdrant-scaling/performance-scaling/SKILL.md b/skills/qdrant-scaling/performance-scaling/SKILL.md
@@ -0,0 +1,67 @@
+---
+name: qdrant-performance-scaling
+description: "Diagnoses and guides Qdrant performance scaling for throughput, latency, IOPS, and memory pressure. Use when someone reports 'need more throughput', 'need lower latency', 'queries timeout', 'IOPS saturated', 'memory too high after scaling', or 'read latency 10x during ingestion'. Also use when performance degrades after scaling or config changes."
+---
+
+# What to Do When Qdrant Performance Needs to Scale
+
+Scaling for throughput and latency are opposite tuning directions. Fewer segments = better throughput. More segments = better latency. Cannot optimize both on the same node.
+
+- Understand the tradeoff [Latency vs throughput](https://qdrant.tech/documentation/guides/optimize/#balancing-latency-and-throughput)
+
+
+## Scaling for Higher RPS
+
+Use when: system can't serve enough queries per second under load.
+
+- Use fewer, larger segments (`default_segment_number: 2`) [Maximizing throughput](https://qdrant.tech/documentation/guides/optimize/#maximizing-throughput)
+- Enable quantization with `always_ram=true` to reduce CPU per query [Quantization](https://qdrant.tech/documentation/guides/quantization/)
+- Add read replicas to distribute query load [Replication](https://qdrant.tech/documentation/guides/distributed_deployment/#replication)
+- Use batch search API to amortize overhead [Batch search](https://qdrant.tech/documentation/concepts/search/#batch-search-api)
+- Configure update throughput control (v1.17+) to prevent unoptimized searches degrading reads [Low latency search](https://qdrant.tech/documentation/guides/low-latency-search/)
+- Set `optimizer_cpu_budget` to limit indexing CPUs (e.g. `2` on an 8-CPU node reserves 6 for queries, `0` = auto, negative = subtract from available)
+
+
+## Scaling for Lower Latency
+
+Use when: individual query latency is too high regardless of load.
+
+- Increase segment count to match CPU cores (`default_segment_number: 16`) [Minimizing latency](https://qdrant.tech/documentation/guides/optimize/#minimizing-latency)
+- Keep quantized vectors and HNSW in RAM (`always_ram=true`) [High precision with speed](https://qdrant.tech/documentation/guides/optimize/#improving-precision)
+- Reduce `hnsw_ef` at query time (trade recall for speed) [Search params](https://qdrant.tech/documentation/guides/optimize/#fine-tuning-search-parameters)
+- Use local NVMe, avoid network-attached storage
+- Configure delayed read fan-out (v1.17+) for tail latency in distributed clusters [Delayed fan-outs](https://qdrant.tech/documentation/guides/low-latency-search/#use-delayed-fan-outs)
+
+
+## Scaling for Disk I/O (IOPS)
+
+Use when: queries timeout despite adequate CPU/RAM, disk throughput saturated. Major production issue.
+
+Symptoms: IOPS near provider limits, high latency during concurrent reads/writes, page cache thrashing.
+
+- Scale out horizontally: each node adds independent IOPS (6 nodes = 6x IOPS vs 1 node)
+- Upgrade to provisioned IOPS or local NVMe
+- Use `io_uring` on Linux (kernel 5.11+) [io_uring article](https://qdrant.tech/articles/io_uring/)
+- Put sparse vectors and text payloads on disk (less IOPS-intensive)
+- Set `indexing_threshold` high during bulk ingestion to defer indexing
+
+
+## Scaling for Memory Pressure
+
+Use when: memory working set >80%, OS cache eviction, OOM errors.
+
+- Vertical scale RAM first. Critical if working set >80%.
+- Set `optimizer_cpu_budget` to limit background optimization CPUs
+- Schedule indexing: set high `indexing_threshold` during peak hours
+- Use quantization: scalar (4x reduction) or binary (16x reduction) [Quantization](https://qdrant.tech/documentation/guides/quantization/)
+- Move payload indexes to disk if filtering is infrequent [On-disk payload index](https://qdrant.tech/documentation/concepts/indexing/#on-disk-payload-index)
+
+[Memory optimization](https://qdrant.tech/documentation/guides/optimize/)
+
+
+## What NOT to Do
+
+- Do not expect to optimize throughput and latency simultaneously on the same node
+- Do not scale horizontally when IOPS-bound without also increasing disk tier
+- Do not run at >90% RAM (OS cache eviction = severe performance degradation)
+- Do not ignore optimizer status during performance debugging
diff --git a/skills/qdrant-scaling/tenant-scaling/SKILL.md b/skills/qdrant-scaling/tenant-scaling/SKILL.md
@@ -0,0 +1,48 @@
+---
+name: qdrant-tenant-scaling
+description: "Guides Qdrant multi-tenant scaling. Use when someone asks 'how to scale tenants', 'one collection per tenant?', 'tenant isolation', 'dedicated shards', or reports tenant performance issues. Also use when multi-tenant workloads outgrow shared infrastructure."
+---
+
+# What to Do When Scaling Multi-Tenant Qdrant
+
+Do not create one collection per tenant. Does not scale past a few hundred and wastes resources. One company hit the 1000 collection limit after a year of collection-per-repo and had to migrate to payload partitioning. Use a shared collection with a tenant key.
+
+- Understand multitenancy patterns [Multitenancy](https://qdrant.tech/documentation/guides/multitenancy/)
+
+
+## Tenants Are Small (< 20k points)
+
+Use when: many tenants with small datasets sharing one deployment.
+
+- Use a tenant ID field with keyword index [Partition by payload](https://qdrant.tech/documentation/guides/multitenancy/#partition-by-payload)
+- Set `is_tenant=true` to co-locate tenant data for sequential reads [Calibrate performance](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-performance)
+- Disable global HNSW (`m: 0`) and use `payload_m: 16` for per-tenant indexes, dramatically faster ingestion [Calibrate performance](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-performance)
+- ACORN (v1.16+) significantly improves multi-tenant filter accuracy at scale [ACORN](https://qdrant.tech/documentation/concepts/search/#acorn-search-algorithm)
+
+Hundreds of millions of points per collection is fine. Split by `org_id % N` only if filter complexity becomes a bottleneck, not for data volume.
+
+
+## Tenants Are Outgrowing Shared Shards
+
+Use when: some tenants have 20k+ points and need dedicated resources.
+
+- Promote tenants from fallback shard to dedicated shard via tenant promotion (v1.16+) [Tiered multitenancy](https://qdrant.tech/documentation/guides/multitenancy/#tiered-multitenancy)
+- Small tenants stay on fallback shards, large tenants get promoted automatically
+- Use dedicated shards via user-defined sharding for full isolation [User-defined sharding](https://qdrant.tech/documentation/guides/distributed_deployment/#user-defined-sharding)
+
+
+## Need Strict Tenant Isolation
+
+Use when: legal/compliance requirements demand per-tenant encryption or strict isolation beyond what payload filtering provides.
+
+- Multiple collections may be necessary for per-tenant encryption keys
+- Limit collection count and use payload filtering within each collection
+- This is the exception, not the default. Only use when compliance requires it.
+
+
+## What NOT to Do
+
+- Do not create one collection per tenant without compliance justification (does not scale past hundreds)
+- Do not skip `is_tenant=true` on the tenant index (kills sequential read performance)
+- Do not build global HNSW for multi-tenant collections (wasteful, use `payload_m` instead)
+- Do not store ColBERT multi-vectors in RAM alongside dense vectors at scale (degrades all queries)
PATCH

echo "Gold patch applied."
