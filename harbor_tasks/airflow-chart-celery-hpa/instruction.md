# Task: Extend Airflow Helm Chart HPA Configuration

## Background

The Apache Airflow Helm chart (located in the repository at `/workspace/airflow`) supports Horizontal Pod Autoscaler (HPA) configuration for Celery workers. Currently, HPA can only be configured via the top-level `workers.hpa` values path.

## Problem

There is no way to configure HPA within the Celery-specific worker subsection. Users who organize their configuration under the `workers.celery` section have no access to HPA settings there. When both the old and new HPA paths are specified, the new path should take precedence.

## Expected Behavior

### Celery worker HPA

When the following values are provided:

```yaml
executor: CeleryExecutor
workers:
  celery:
    hpa:
      enabled: true
```

The chart should render a `HorizontalPodAutoscaler` resource. This must also work with `CeleryKubernetesExecutor`.

### Replica counts

When `minReplicaCount` and `maxReplicaCount` are specified under the celery HPA config:

```yaml
workers:
  celery:
    hpa:
      enabled: true
      minReplicaCount: 2
      maxReplicaCount: 10
```

The rendered HPA should have `spec.minReplicas: 2` and `spec.maxReplicas: 10`.

### Default metrics

When HPA is enabled under the celery path but no custom metrics are provided, the rendered HPA must have exactly this `spec.metrics`:

```yaml
- type: Resource
  resource:
    name: cpu
    target:
      type: Utilization
      averageUtilization: 80
```

### Custom metrics

Custom `metrics` specified under the celery HPA config should be passed through to `spec.metrics` on the rendered HPA.

### Scaling behavior

Custom `behavior` specified under the celery HPA config should be passed through to `spec.behavior` on the rendered HPA.

### Executor gating

HPA resources should only be rendered for `CeleryExecutor` and `CeleryKubernetesExecutor`. For other executors (e.g., `KubernetesExecutor`), no HPA should be created even if the celery HPA config is enabled.

### KEDA mutual exclusion

When KEDA is enabled under the celery worker section (`workers.celery.keda.enabled: true`), only a `ScaledObject` resource should appear in the rendered output. No HPA resource should be created, even if the celery HPA config is also enabled.

### Scale target reference

The HPA's `scaleTargetRef.kind` depends on persistence:

- When `workers.celery.persistence.enabled` is `true` → `StatefulSet`
- When `workers.celery.persistence.enabled` is `false` → `Deployment`

### Backward compatibility

The existing `workers.hpa.enabled` path must continue to work unchanged. When only the old path is set, HPA should render exactly as before.

### Worker sets

The chart supports multiple Celery worker sets via `workers.celery.sets` (a list of objects with `name` fields). When `workers.celery.enableDefault` is `false` and a worker set has its own HPA configuration, an HPA resource should be created for that worker set. Example:

```yaml
workers:
  celery:
    enableDefault: false
    sets:
      - name: test
        hpa:
          enabled: true
          minReplicaCount: 15
```

This should produce a single HPA resource with `spec.minReplicas: 15`.

### HPA disabled by default

When neither HPA config path is explicitly enabled, no HPA resource should be rendered.

### JSON Schema

The chart's JSON schema must:

- Define an HPA section within the celery worker configuration containing properties: `enabled`, `minReplicaCount`, `maxReplicaCount`, `metrics`, `behavior`
- The old `workers.hpa` section's description must contain the word "deprecated"

The chart's existing test suites must also continue to pass after the changes.

## Testing

Run tests with: `pytest /tests/test_outputs.py -v`
