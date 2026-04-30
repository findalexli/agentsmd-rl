#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "- Use `/healthz`, `/livez`, `/readyz` for basic status, liveness, and readiness " "skills/qdrant-monitoring/setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-monitoring/setup/SKILL.md b/skills/qdrant-monitoring/setup/SKILL.md
@@ -17,13 +17,6 @@ Use when: setting up metric collection for the first time or adding a new deploy
 - Prefix customization via `service.metrics_prefix` config or `QDRANT__SERVICE__METRICS_PREFIX` env var
 - Example self-hosted setup with Prometheus + Grafana [prometheus-monitoring repo](https://github.com/qdrant/prometheus-monitoring)
 
-Key metric categories:
-- **Collection**: point counts, vector counts, replica status, pending optimizations
-- **API response**: `rest_responses_avg_duration_seconds`, `rest_responses_duration_seconds` (histogram, v1.8+), failure rates. `grpc_responses_` prefix for gRPC
-- **Process**: memory allocation, threads, file descriptors, page faults
-- **Cluster**: Raft consensus state (distributed mode only)
-- **Snapshot**: creation and recovery progress
-
 
 ## Hybrid Cloud Scraping
 
@@ -39,10 +32,7 @@ Do not just scrape Qdrant nodes. In Hybrid Cloud, you manage the Kubernetes data
 
 Use when: configuring Kubernetes health checks.
 
-- `/healthz` for basic status
-- `/livez` for liveness probe (is the process alive)
-- `/readyz` for readiness probe (is the node ready to serve traffic)
-- Full list of health endpoints [Kubernetes health endpoints](https://qdrant.tech/documentation/guides/monitoring/#kubernetes-health-endpoints)
+- Use `/healthz`, `/livez`, `/readyz` for basic status, liveness, and readiness [Kubernetes health endpoints](https://qdrant.tech/documentation/guides/monitoring/#kubernetes-health-endpoints)
 
 
 ## Alerting
PATCH

echo "Gold patch applied."
