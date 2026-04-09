# Task: Add workers.celery.affinity & workers.kubernetes.affinity

## Problem

The Airflow Helm chart currently has a single `workers.affinity` field that applies to both:
1. Celery worker pods (when using CeleryExecutor)
2. Pods created via pod-template-file (when using KubernetesExecutor)

This conflates two different use cases and doesn't allow users to specify different affinity rules for each executor type.

## Goal

Split the `workers.affinity` field into two new fields:
- `workers.celery.affinity` - for Celery worker pods only
- `workers.kubernetes.affinity` - for Kubernetes executor pod template only

The old `workers.affinity` field should be deprecated but still work for backward compatibility.

## Files to Modify

1. **`chart/files/pod-template-file.kubernetes-helm-yaml`** - Update the affinity template logic to use `workers.kubernetes.affinity` with fallback to `workers.affinity`

2. **`chart/values.schema.json`** - Add schema definitions for the two new affinity fields and update the description of the deprecated `workers.affinity` field

3. **`chart/values.yaml`** - Add the new affinity fields with default empty values and deprecation comments

4. **`chart/templates/NOTES.txt`** - Add a deprecation warning that appears when `workers.affinity` is used

5. **`chart/newsfragments/64860.significant.rst`** - Create a newsfragment documenting the significant change

## Key Requirements

1. **Precedence**: When both old and new fields are set, the new field should take precedence:
   - For pod-template-file: `workers.kubernetes.affinity` > `workers.affinity` > global `affinity`
   - For worker deployment: `workers.celery.affinity` > `workers.affinity`

2. **Backward Compatibility**: The old `workers.affinity` field should still work exactly as before

3. **Schema**: New fields must be properly typed with the k8s Affinity reference

4. **Deprecation Notice**: Users should be warned when using the deprecated field

## Testing

The tests will verify:
- `workers.kubernetes.affinity` is correctly applied to pod-template-file
- `workers.celery.affinity` is correctly applied to worker deployment
- Precedence works correctly (new fields override old fields)
- Backward compatibility is maintained (old field still works)
- Helm lint passes
- Helm template works with default values
