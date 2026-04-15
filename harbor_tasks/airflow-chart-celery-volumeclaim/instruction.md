# Add workers.celery.volumeClaimTemplates to Airflow Helm Chart

## Problem

The Airflow Helm chart currently provides a `workers.volumeClaimTemplates` configuration option. However, volume claim templates are specifically for Celery workers (not for Kubernetes executor workers). A new `workers.celery.volumeClaimTemplates` field should be added for better organization, while maintaining backward compatibility with the existing location and marking the old location as deprecated.

## Requirements

### 1. New field in values.yaml

Add a `volumeClaimTemplates` field under the `workers.celery` section in `chart/values.yaml`. The `workers.celery` section already contains the fields: `enableDefault`, `persistence`, `hostAliases`, and `schedulerName`. The new field should be placed alongside these existing fields.

- The default value must be an empty list (`[]`)
- The field must have a documentation comment containing either the phrase "Additional volume claim templates" or "Requires mounting"

### 2. Deprecation comment on old field

The existing `workers.volumeClaimTemplates` field in `chart/values.yaml` must have a deprecation comment with the exact text:

```
# (deprecated, use `workers.celery.volumeClaimTemplates` instead)
```

### 3. JSON schema update

Update `chart/values.schema.json`:

- Add `workers.celery.volumeClaimTemplates` with:
  - Type: `"array"`
  - A `"description"` field
  - At least 2 entries in `"examples"`
  - Each example must contain the keys: `name`, `storageClassName`, `accessModes`, and `resources`
- Update the old `workers.volumeClaimTemplates` description to include the word "deprecated" and reference `workers.celery.volumeClaimTemplates` as the replacement

### 4. Deprecation warning in NOTES.txt

Add a deprecation warning in `chart/templates/NOTES.txt` that:

- Contains the exact text: `` `workers.volumeClaimTemplates` has been renamed ``
- References `workers.celery.volumeClaimTemplates` as the new location

### 5. Newsfragment

Create the file `chart/newsfragments/62048.significant.rst` documenting the deprecation and migration path.

## Backward Compatibility

The chart must still render correctly with:

- Only the old `workers.volumeClaimTemplates` (backward compatibility)
- Only the new `workers.celery.volumeClaimTemplates`
- Both specified simultaneously (new location takes precedence)

## Testing

To verify rendering:

```bash
cd /workspace/airflow/chart
helm dependency build
helm template test . --values <values-file>
```

## Notes

- Look at how other fields are organized under `workers.celery` for consistency
- The deprecation warning should follow the same format as other deprecation warnings in NOTES.txt
