#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: \"Guides Qdrant monitoring and observability setup. Use when someone" "skills/qdrant-monitoring/SKILL.md" && grep -qF "description: \"Diagnoses Qdrant production issues using metrics and observability" "skills/qdrant-monitoring/debugging/SKILL.md" && grep -qF "description: \"Guides Qdrant monitoring setup including Prometheus scraping, heal" "skills/qdrant-monitoring/setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-monitoring/SKILL.md b/skills/qdrant-monitoring/SKILL.md
@@ -1,43 +1,24 @@
 ---
 name: qdrant-monitoring
-description: "Qdrant provides monitoring and observability tools available for both self-hosted and cloud deployments. This document provides an overview of monitoring options and best practices for monitoring Qdrant performance and health."
+description: "Guides Qdrant monitoring and observability setup. Use when someone asks 'how to monitor Qdrant', 'what metrics to track', 'is Qdrant healthy', 'optimizer stuck', 'why is memory growing', 'requests are slow', or needs to set up Prometheus, Grafana, or health checks. Also use when debugging production issues that require metric analysis."
 allowed-tools:
   - Read
   - Grep
   - Glob
 ---
 
-
-
 # Qdrant Monitoring
 
-Qdrant monitoring allows to track the performance and health of your Qdrant deployment, and to identify and troubleshoot issues.
-Monitoring is available for both self-hosted and cloud deployments of Qdrant, though Cloud deployment provides more advanced monitoring features out of the box.
-
-
-## Prometheus Metrics
-
-Qdrant exposes internal metrics in Prometheus format, which can be scraped by Prometheus server from `/metrics` endpoint.
-In addition to Qdrant instance-level metrics, Qdrant cluster also provides cluster-level metrics, available on `/sys_metrics` endpoint.
-
-Example of self-hosted monitoring of Qdrant Cloud cluster can be found in [repository](https://github.com/qdrant/prometheus-monitoring)
-
-
-## Liveness and Readiness Probes
-
-<!-- ToDo: Improve docs about `/readyz` -->
-
-Read about liveness and readiness probes [here](https://qdrant.tech/documentation/guides/monitoring/#kubernetes-health-endpoints)
+Qdrant monitoring allows tracking performance and health of your deployment, and identifying issues before they become outages. First determine whether you need to set up monitoring or diagnose an active issue.
 
-## Optimization process observability
+- Understand available metrics [Monitoring docs](https://qdrant.tech/documentation/guides/monitoring/)
 
-<!-- ToDo -->
 
-## Memory usage observability
+## Monitoring Setup
 
-<!-- ToDo -->
+Prometheus scraping, health probes, Hybrid Cloud specifics, alerting, and log centralization. [Monitoring Setup](setup/SKILL.md)
 
-## Slow requests observability
 
-<!-- ToDo -->
+## Debugging with Metrics
 
+Optimizer stuck, memory growth, slow requests. Using metrics to diagnose active production issues. [Debugging with Metrics](debugging/SKILL.md)
diff --git a/skills/qdrant-monitoring/debugging/SKILL.md b/skills/qdrant-monitoring/debugging/SKILL.md
@@ -0,0 +1,52 @@
+---
+name: qdrant-monitoring-debugging
+description: "Diagnoses Qdrant production issues using metrics and observability tools. Use when someone reports 'optimizer stuck', 'indexing too slow', 'memory too high', 'OOM crash', 'queries are slow', 'latency spike', or 'search was fast now it's slow'. Also use when performance degrades without obvious config changes."
+---
+
+# How to Debug Qdrant with Metrics
+
+First check optimizer status. Most production issues trace back to active optimizations competing for resources. If optimizer is clean, check memory, then request metrics.
+
+
+## Optimizer Stuck or Too Slow
+
+Use when: optimizer running for hours, not finishing, or showing errors.
+
+- Use `/collections/{collection_name}/optimizations` endpoint (v1.17+) to check status [Optimization monitoring](https://qdrant.tech/documentation/concepts/optimizer/#optimization-monitoring)
+- Query with optional detail flags: `?with=queued,completed,idle_segments`
+- Returns: queued optimizations count, active optimizer type, involved segments, progress tracking
+- Web UI has an Optimizations tab with timeline view and per-task duration metrics [Web UI](https://qdrant.tech/documentation/concepts/optimizer/#web-ui)
+- If `optimizer_status` shows an error in collection info, check logs for disk full or corrupted segments
+- Large merges and HNSW rebuilds legitimately take hours on big datasets. Check progress before assuming it's stuck.
+
+
+## Memory Seems Too High
+
+Use when: memory exceeds expectations, node crashes with OOM, or memory keeps growing.
+
+- Process memory metrics available via `/metrics` (RSS, allocated bytes, page faults)
+- Qdrant uses two types of RAM: resident memory (data structures, quantized vectors) and OS page cache (cached disk reads). Page cache filling available RAM is normal. [Memory article](https://qdrant.tech/articles/memory-consumption/)
+- If resident memory (RSSAnon) exceeds 80% of total RAM, investigate
+- Check `/telemetry` for per-collection breakdown of point counts and vector configurations
+- Estimate expected memory: `num_vectors * dimensions * 4 bytes * 1.5` for vectors, plus payload and index overhead [Capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/)
+- Common causes of unexpected growth: quantized vectors with `always_ram=true`, too many payload indexes, large `max_segment_size` during optimization
+
+
+## Queries Are Slow
+
+Use when: queries slower than expected and you need to identify the cause.
+
+- Track `rest_responses_avg_duration_seconds` and `rest_responses_max_duration_seconds` per endpoint
+- Use histogram metric `rest_responses_duration_seconds` (v1.8+) for percentile analysis in Grafana
+- Equivalent gRPC metrics with `grpc_responses_` prefix
+- Check optimizer status first. Active optimizations compete for CPU and I/O, degrading search latency.
+- Check segment count via collection info. Too many unmerged segments after bulk upload causes slower search.
+- Compare filtered vs unfiltered query times. Large gap means missing payload index. [Payload index](https://qdrant.tech/documentation/concepts/indexing/#payload-index)
+
+
+## What NOT to Do
+
+- Ignore optimizer status when debugging slow queries (most common root cause)
+- Assume memory leak when page cache fills RAM (normal OS behavior)
+- Make config changes while optimizer is running (causes cascading re-optimizations)
+- Blame Qdrant before checking if bulk upload just finished (unmerged segments)
diff --git a/skills/qdrant-monitoring/setup/SKILL.md b/skills/qdrant-monitoring/setup/SKILL.md
@@ -0,0 +1,71 @@
+---
+name: qdrant-monitoring-setup
+description: "Guides Qdrant monitoring setup including Prometheus scraping, health probes, Hybrid Cloud metrics, alerting, and log centralization. Use when someone asks 'how to set up monitoring', 'Prometheus config', 'Grafana dashboard', 'health check endpoints', 'how to scrape Hybrid Cloud', 'what alerts to set', 'how to centralize logs', or 'audit logging'."
+---
+
+# How to Set Up Qdrant Monitoring
+
+Get Prometheus scraping working first, then health probes, then alerting. Do not skip monitoring setup before going to production.
+
+
+## Prometheus Metrics
+
+Use when: setting up metric collection for the first time or adding a new deployment.
+
+- Node metrics at `/metrics` endpoint [Monitoring docs](https://qdrant.tech/documentation/guides/monitoring/)
+- Cluster metrics at `/sys_metrics` (Qdrant Cloud only)
+- Prefix customization via `service.metrics_prefix` config or `QDRANT__SERVICE__METRICS_PREFIX` env var
+- Example self-hosted setup with Prometheus + Grafana [prometheus-monitoring repo](https://github.com/qdrant/prometheus-monitoring)
+
+Key metric categories:
+- **Collection**: point counts, vector counts, replica status, pending optimizations
+- **API response**: `rest_responses_avg_duration_seconds`, `rest_responses_duration_seconds` (histogram, v1.8+), failure rates. `grpc_responses_` prefix for gRPC
+- **Process**: memory allocation, threads, file descriptors, page faults
+- **Cluster**: Raft consensus state (distributed mode only)
+- **Snapshot**: creation and recovery progress
+
+
+## Hybrid Cloud Scraping
+
+Use when: running Qdrant Hybrid Cloud and need cluster-level visibility.
+
+Do not just scrape Qdrant nodes. In Hybrid Cloud, you manage the Kubernetes data plane. You must also scrape the cluster-exporter and operator pods for full cluster visibility and operator state.
+
+- Hybrid Cloud Prometheus setup tutorial [Hybrid Cloud Prometheus](https://qdrant.tech/documentation/tutorials-and-examples/hybrid-cloud-prometheus/)
+- Official Grafana dashboards [Grafana dashboard repo](https://github.com/qdrant/qdrant-cloud-grafana-dashboard)
+
+
+## Liveness and Readiness Probes
+
+Use when: configuring Kubernetes health checks.
+
+- `/healthz` for basic status
+- `/livez` for liveness probe (is the process alive)
+- `/readyz` for readiness probe (is the node ready to serve traffic)
+- Full list of health endpoints [Kubernetes health endpoints](https://qdrant.tech/documentation/guides/monitoring/#kubernetes-health-endpoints)
+
+
+## Alerting
+
+Use when: setting up alerts for production or Hybrid Cloud deployments.
+
+- Hybrid Cloud provides ~11 pre-configured Prometheus alerts out of the box [Cloud cluster monitoring](https://qdrant.tech/documentation/cloud/cluster-monitoring/)
+- Use AlertmanagerConfig to route alerts to Slack, PagerDuty, or other targets based on labels
+- At minimum, alert on: optimizer errors, node not ready, replication factor below target, disk usage >80%
+
+
+## Log Centralization and Audit Logging
+
+Use when: enterprise compliance requires centralized logs or audit trails.
+
+- Enable JSON log format for structured analysis: set `logger.format` to `json` in config [Configuration](https://qdrant.tech/documentation/guides/configuration/)
+- Use FluentD/OpenSearch for log aggregation
+- Audit logs (v1.17+) write to local filesystem (`/qdrant/storage/audit/`), not stdout. Mount a Persistent Volume and deploy a sidecar container to tail these files to stdout so DaemonSets can pick them up. [Audit logging](https://qdrant.tech/documentation/operations/security/#audit-logging)
+
+
+## What NOT to Do
+
+- Scrape `/sys_metrics` on self-hosted (only available on Qdrant Cloud)
+- Scrape only Qdrant nodes in Hybrid Cloud (miss cluster-exporter and operator metrics)
+- Skip monitoring setup before going to production (you will regret it)
+- Alert on page cache memory usage (it's supposed to fill available RAM, normal OS behavior)
PATCH

echo "Gold patch applied."
