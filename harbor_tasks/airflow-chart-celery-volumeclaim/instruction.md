# Add workers.celery.volumeClaimTemplates to Airflow Helm Chart

## Problem

The Airflow Helm chart's `workers.volumeClaimTemplates` configuration option is located at the top level of the workers section. However, volume claim templates are specifically for Celery workers (not for Kubernetes executor workers). This creates confusion and inconsistent configuration.

The goal is to:
1. Add a new `workers.celery.volumeClaimTemplates` field for better organization
2. Maintain backward compatibility with the existing `workers.volumeClaimTemplates`
3. Mark the old location as deprecated with appropriate warnings

## What You Need to Do

1. **Add the new field location** in `chart/values.yaml`:
   - Add `volumeClaimTemplates: []` under `workers.celery`
   - Include proper documentation comments explaining the purpose

2. **Update the JSON schema** in `chart/values.schema.json`:
   - Add `workers.celery.volumeClaimTemplates` with proper type, description, and examples
   - Update the description of the old `workers.volumeClaimTemplates` to indicate deprecation

3. **Add deprecation warning** in `chart/templates/NOTES.txt`:
   - When `workers.volumeClaimTemplates` is used, show a deprecation warning
   - Direct users to use the new `workers.celery.volumeClaimTemplates` instead

4. **Create newsfragment** at `chart/newsfragments/62048.significant.rst`:
   - Document the deprecation and migration path

## Key Files to Modify

- `chart/values.yaml` - Add new field location
- `chart/values.schema.json` - Update schema for both old and new locations
- `chart/templates/NOTES.txt` - Add deprecation warning
- `chart/newsfragments/62048.significant.rst` - Create this file

## Testing

The chart should still render correctly with both:
- The old `workers.volumeClaimTemplates` (backward compatibility)
- The new `workers.celery.volumeClaimTemplates`
- Both specified (new location takes precedence)

To test rendering:
```bash
cd /workspace/airflow/chart
helm dependency build
helm template test . --values <values-file>
```

## Notes

- Look at how other fields are organized under `workers.celery` for consistency
- The examples in schema.json should show realistic volume claim templates
- The deprecation warning should follow the same format as other deprecation warnings in NOTES.txt
