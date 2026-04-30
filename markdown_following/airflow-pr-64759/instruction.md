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

The Helm values schema should include descriptions for the new fields, and a deprecation warning should inform users who still use the old `workers.schedulerName` option.

## Code Style Requirements

When modifying JSON Schema files (`values.schema.json`), each property addition should include a `description` field explaining its purpose. Deprecated fields must have their description updated to include a deprecation notice mentioning the replacement fields.
