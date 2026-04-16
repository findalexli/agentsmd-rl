# Task: Add Celery-specific waitForMigrations configuration to Airflow Helm Chart

## Problem

The Airflow Helm chart currently has a `workers.waitForMigrations` configuration section that controls the wait-for-airflow-migrations init container for Celery workers. However, this configuration is located at the wrong level in the config hierarchy.

To align with other Celery-specific settings that already exist under `workers.celery.*`, the `waitForMigrations` configuration should also be available at `workers.celery.waitForMigrations`.

## What needs to be done

1. Add a new `workers.celery.waitForMigrations` configuration section with the same properties as the existing `workers.waitForMigrations`:
   - `enabled`: Whether to create the init container. The schema type for this field must allow `null` to support inheritance from the deprecated path.
   - `env`: Additional environment variables for the init container (array type)
   - `securityContexts.container`: Security context for the init container

2. The new path should take precedence when both old and new paths are specified.

3. Mark the old `workers.waitForMigrations` path as deprecated with appropriate notices:
   - Add "deprecated" to the schema descriptions for the old path
   - The NOTES.txt template should display deprecation warnings mentioning both the old paths (`workers.waitForMigrations.enabled`, `workers.waitForMigrations.env`) and their replacements (`workers.celery.waitForMigrations.enabled`, `workers.celery.waitForMigrations.env`)

4. Update the Helm chart templates to recognize the new configuration path.

5. Create a newsfragment file named `62054.significant.rst` in `chart/newsfragments/` describing the deprecation and migration path from `workers.waitForMigrations` to `workers.celery.waitForMigrations`.

## Files to examine

- `chart/values.yaml` - Default values configuration
- `chart/values.schema.json` - JSON schema for values validation
- `chart/templates/NOTES.txt` - Post-install notes and deprecation warnings
- `chart/templates/workers/worker-deployment.yaml` - Worker deployment template (references waitForMigrations)

## Acceptance criteria

- New `workers.celery.waitForMigrations` section exists in both values.yaml and values.schema.json
- The `enabled` field in the new schema path has a type that includes `null` for backward compatibility inheritance
- The new configuration path functions correctly (can disable init container, set env vars, set security context)
- Old configuration path still works for backward compatibility
- Deprecation warnings are shown when users use the old path
- Schema descriptions for the old path contain "deprecated" and reference the new path
- NOTES.txt contains deprecation warnings that mention both `workers.waitForMigrations.enabled` and `workers.celery.waitForMigrations.enabled`, as well as `workers.waitForMigrations.env` and `workers.celery.waitForMigrations.env`
- Newsfragment file `62054.significant.rst` exists and documents the configuration path change
