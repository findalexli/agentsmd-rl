# Task: Add workers.celery.hpa configuration to Airflow Helm chart

## Problem

The Airflow Helm chart has a `workers.hpa` configuration section for Horizontal Pod Autoscaler settings, but this configuration only applies to Celery workers. The current location is misleading because:

1. The `workers.hpa` path suggests it applies to all workers, but HPA is only relevant for Celery executors
2. Users configuring Kubernetes executor workers might mistakenly think HPA applies to them
3. The naming doesn't follow the pattern of other Celery-specific settings

## Symptoms

- The `workers.hpa` configuration works, but its scope is unclear from the path
- There's no `workers.celery.hpa` section that would clearly indicate Celery-specific HPA settings
- When users set `workers.celery.hpa.enabled: true`, nothing happens because the configuration path doesn't exist

## Expected Behavior

1. A new `workers.celery.hpa` configuration section should exist in `chart/values.yaml` with an `enabled` property (and other HPA options), structured under `workers:` → `celery:` → `hpa:`
2. The `chart/values.schema.json` should define the `workers.celery.hpa` schema with the following properties: `enabled`, `minReplicaCount`, `maxReplicaCount`, `metrics`, and `behavior`
3. `chart/templates/NOTES.txt` should contain deprecation warnings for the old `workers.hpa` path, specifically mentioning:
   - `workers.hpa.enabled` (with a reference to `workers.celery.hpa.enabled` as the new location)
   - `workers.hpa.minReplicaCount`
   - `workers.hpa.maxReplicaCount`
4. The old `workers.hpa` should still work for backward compatibility, but users should be informed it's deprecated

## Files to Investigate

- `chart/values.yaml` - Main Helm values file
- `chart/values.schema.json` - JSON schema for values validation
- `chart/templates/NOTES.txt` - Post-install notes (for deprecation warnings)
- `chart/templates/workers/worker-deployment.yaml` - Worker deployment template

## Constraints

- Maintain full backward compatibility with existing `workers.hpa` configurations
- Follow the existing patterns in the Helm chart for configuration structure
- Ensure the schema properly validates the new configuration options
