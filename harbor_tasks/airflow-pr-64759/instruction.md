# Helm Chart: Add Separate Scheduler Name Options for Workers

## Problem

The Airflow Helm chart currently uses a single `workers.schedulerName` configuration option that applies to both Celery worker pods and Kubernetes executor pod templates. This is limiting for users who need different Kubernetes scheduler configurations for these two distinct workload types.

For example, a user may want to use:
- `most-allocated` scheduler for Celery workers (long-running pods)
- `default-scheduler` for Kubernetes executor pods (short-lived task pods)

Currently, there's no way to configure these separately.

## Expected Behavior

The chart should support:
1. `workers.kubernetes.schedulerName` - scheduler name for pods created via pod-template-file (Kubernetes executor)
2. `workers.celery.schedulerName` - scheduler name for Celery worker deployments

The priority order should be:
- For pod-template-file: `workers.kubernetes.schedulerName` > `workers.schedulerName` > `schedulerName`
- For Celery workers: `workers.celery.schedulerName` > `workers.schedulerName` > `schedulerName`

The old `workers.schedulerName` should remain as a deprecated fallback for backward compatibility.

## Files to Investigate

- `chart/files/pod-template-file.kubernetes-helm-yaml` - Pod template for Kubernetes executor
- `chart/values.yaml` - Default Helm values
- `chart/values.schema.json` - JSON schema for values validation
- `chart/templates/NOTES.txt` - Deprecation warnings

## Requirements

1. Update the pod-template-file to check `workers.kubernetes.schedulerName` first
2. Add the new scheduler name fields to `values.yaml` with null defaults
3. Add JSON schema definitions for the new fields in `values.schema.json`
4. Mark the old `workers.schedulerName` as deprecated in the schema description
5. Add a deprecation warning in `NOTES.txt` when the old option is used
