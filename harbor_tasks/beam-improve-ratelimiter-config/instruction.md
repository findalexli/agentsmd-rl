# Improve Envoy Rate Limiter Terraform Configuration

## Problem

The Terraform module in `examples/terraform/envoy-ratelimiter/` deploys all Kubernetes resources into the `default` namespace — there is no way to specify a custom namespace. This makes it hard to organize resources or run multiple instances in the same cluster.

Additionally, the StatsD exporter sidecar container is always deployed alongside the rate limiter, even when metrics collection is not needed. This wastes resources in environments where Prometheus scraping isn't configured.

The README only lists Python pipeline examples but the rate limiter also works with Java pipelines.

## Expected Behavior

1. **Namespace support**: Add a configurable Kubernetes namespace variable. All resources (ConfigMap, Redis, Rate Limiter deployment/services, HPA) should be deployed into this namespace. A `kubernetes_namespace` resource should be created to ensure the namespace exists.

2. **Conditional metrics sidecar**: The statsd-exporter sidecar container should only be deployed when metrics collection is explicitly enabled. The `USE_STATSD` environment variable on the ratelimit container should reflect this setting. When metrics are disabled, the metrics port should also be removed from the service definitions.

3. **Documentation**: After making the code changes, update the README to document the new variables and add Java pipeline examples.

## Files to Look At

- `examples/terraform/envoy-ratelimiter/ratelimit.tf` — main resource definitions
- `examples/terraform/envoy-ratelimiter/variables.tf` — input variable declarations
- `examples/terraform/envoy-ratelimiter/README.md` — module documentation with variable reference table
