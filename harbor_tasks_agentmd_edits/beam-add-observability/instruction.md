# Add Observability to Envoy Rate Limiter

## Problem

The Envoy Rate Limiter Terraform module under `examples/terraform/envoy-ratelimiter/` currently uses a **StatsD exporter sidecar** container to expose metrics in Prometheus format on port 9102. This approach is outdated — the Envoy ratelimit service natively supports Prometheus metrics, making the sidecar unnecessary overhead. Additionally, the metrics are not being exported to Google Cloud Monitoring, so there's no way to view them in the GCP console.

The deployment process also lacks a helper script, requiring users to manually run multiple Terraform commands in the correct order.

## Expected Behavior

1. **Replace StatsD with native Prometheus metrics**: The ratelimit container should expose Prometheus metrics directly (on port 9090) instead of relying on a separate statsd-exporter sidecar. The `USE_PROMETHEUS` env var should be configured, and the old `STATSD_HOST`/`STATSD_PORT` env vars and statsd-exporter container should be removed.

2. **Export metrics to Cloud Monitoring**: Add a `PodMonitoring` custom resource that scrapes the Prometheus endpoint and exports metrics to Google Cloud Monitoring. The `monitoring` API should be enabled in `prerequisites.tf`.

3. **Update defaults**: The `enable_metrics` variable should default to `true` (was `false`) since observability should be on by default.

4. **Add a deploy helper script**: Create a `deploy.sh` script that automates the deployment process (init, create cluster, deploy resources) and supports both `apply` and `destroy` commands.

5. **Update the README**: After making the code changes, update the project's README.md to reflect the new metrics architecture, document the deploy script usage, and add an observability section describing available metrics and how to view them in GCP. The variables table should also be updated.

## Files to Look At

- `examples/terraform/envoy-ratelimiter/ratelimit.tf` — Main Kubernetes deployment and service definitions
- `examples/terraform/envoy-ratelimiter/prerequisites.tf` — Required GCP APIs
- `examples/terraform/envoy-ratelimiter/variables.tf` — Terraform variable definitions
- `examples/terraform/envoy-ratelimiter/README.md` — Project documentation (needs updating)
