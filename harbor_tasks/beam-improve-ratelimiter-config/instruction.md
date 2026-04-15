# Improve Envoy Rate Limiter Terraform Configuration

## Problem

The Terraform module in `examples/terraform/envoy-ratelimiter/` deploys all Kubernetes resources into the `default` namespace — there is no way to specify a custom namespace. This makes it hard to organize resources or run multiple instances in the same cluster.

Additionally, the StatsD exporter sidecar container is always deployed alongside the rate limiter, even when metrics collection is not needed. This wastes resources in environments where Prometheus scraping isn't configured.

The README only lists Python pipeline examples but the rate limiter also works with Java pipelines.

## Expected Behavior

1. **Namespace support**: Add a configurable Kubernetes namespace variable. All resources (ConfigMap, Redis, Rate Limiter deployment/services, HPA) should be deployed into this namespace. A `kubernetes_namespace` resource should be created to ensure the namespace exists.

2. **Conditional metrics sidecar**: The statsd-exporter sidecar container should only be deployed when metrics collection is explicitly enabled. The `USE_STATSD` environment variable on the ratelimit container should reflect this setting. When metrics are disabled, the metrics port should also be removed from the service definitions.

3. **Documentation**: After making the code changes, update the README to document the new variables and add Java pipeline examples.

## Terraform Module Structure

The module uses the following Terraform files in `examples/terraform/envoy-ratelimiter/`:

- `ratelimit.tf` — main Kubernetes resource definitions (ConfigMap, Redis, Rate Limiter, HPA, services)
- `variables.tf` — input variable declarations
- `gke.tf` — GKE cluster configuration with private cluster support
- `outputs.tf` — output values including cluster name and load balancer IP
- `prerequisites.tf` — GCP project services and API enablement
- `provider.tf` — Terraform provider configuration
- `README.md` — module documentation

## Required Variables (variables.tf)

The following variables must be defined in `variables.tf`:

- `project_id` — GCP project ID
- `vpc_name` — VPC network name
- `subnet_name` — subnet name
- `ratelimit_config_yaml` — rate limit configuration YAML
- A **namespace** variable (string type, default `"envoy-ratelimiter"`) to specify the Kubernetes namespace for deployment
- An **enable_metrics** variable (boolean type, default `false`) to control whether the statsd-exporter sidecar is deployed

## Required Outputs (outputs.tf)

The module must define the following outputs in `outputs.tf`:

- `cluster_name` — the GKE cluster name
- `load_balancer_ip` — the external load balancer IP address

## gke.tf Requirements

The GKE cluster resource must include `private_cluster_config` block and reference the following variables: `var.cluster_name`, `var.control_plane_cidr`, `var.deletion_protection`.

## Kubernetes Resources (ratelimit.tf)

The following Kubernetes resources must exist in `ratelimit.tf`:

- `kubernetes_deployment` named `ratelimit`
- `kubernetes_deployment` named `redis`
- `kubernetes_service` named `ratelimit`
- `kubernetes_service` named `redis`
- `kubernetes_config_map` named `ratelimit_config`
- `kubernetes_horizontal_pod_autoscaler_v2`

All Kubernetes resources must set `namespace = var.<namespace_var>` where `<namespace_var>` is the namespace variable defined in variables.tf.

## Conditional Metrics Sidecar

The statsd-exporter sidecar container must only be deployed when metrics are enabled. This requires using Terraform's `dynamic` block with `for_each` gated on the enable_metrics variable. When metrics are disabled, the `USE_STATSD` environment variable must be set to `"false"`.

## Files to Modify

- `examples/terraform/envoy-ratelimiter/ratelimit.tf` — add namespace resources, conditional sidecar
- `examples/terraform/envoy-ratelimiter/variables.tf` — add namespace and enable_metrics variables
- `examples/terraform/envoy-ratelimiter/README.md` — document new variables and add Java examples