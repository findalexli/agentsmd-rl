# Deprecate `workers.volumeClaimTemplates` in favor of `workers.celery.volumeClaimTemplates`

## Problem

In the Airflow Helm chart, Celery worker volume claim templates are configured at `workers.volumeClaimTemplates` in `values.yaml`. This path is inconsistent with other Celery worker settings (`workers.celery.persistence`, `workers.celery.replicas`, etc.) which live under `workers.celery`.

The `workers.volumeClaimTemplates` path should be deprecated in favor of a new canonical path `workers.celery.volumeClaimTemplates`. The old path must continue to work for backward compatibility.

## Scope

The following files are involved:
- `chart/values.yaml`
- `chart/values.schema.json`
- `chart/templates/NOTES.txt`
- `chart/newsfragments/` (new fragment)
- `helm-tests/tests/helm_tests/airflow_core/test_worker.py`
- `helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py`

## Acceptance Criteria

1. **New field**: A `volumeClaimTemplates` field must exist under `workers.celery` in `values.yaml`, defaulting to an empty list (`[]`). The section should include commented-out examples referencing volumes named `data-volume-1` (with storage class `storage-class-1`) and `data-volume-2` (with storage class `storage-class-2`).

2. **Legacy deprecation**: The existing `workers.volumeClaimTemplates` field in `values.yaml` should indicate it is deprecated. The file content must include the word "deprecated" (case-insensitive) and reference the new path `workers.celery.volumeClaimTemplates`.

3. **JSON Schema** (`values.schema.json`): The `workers.celery` section should have a `volumeClaimTemplates` property of type `"array"` with at least 2 examples. The legacy `workers.volumeClaimTemplates` property's description must contain "deprecated" (case-insensitive) and reference `workers.celery.volumeClaimTemplates`. The schema definitions must include `io.k8s.api.core.v1.PersistentVolumeClaimTemplate`.

4. **Deprecation warning** (`NOTES.txt`): When `workers.volumeClaimTemplates` is non-empty, the rendered output should display a warning containing the exact header `DEPRECATION WARNING`, the old path `workers.volumeClaimTemplates`, and the new path `workers.celery.volumeClaimTemplates`.

5. **Newsfragment**: A file named `62048.significant.rst` must exist in `chart/newsfragments/` documenting the deprecation. Its content must include the word "deprecated" and reference both `workers.volumeClaimTemplates` and `workers.celery.volumeClaimTemplates`.

6. **Test updates**:
   - `test_worker.py`: The volume claim template test should use `pytest.mark.parametrize` to cover both the legacy path and the new `workers.celery.volumeClaimTemplates` path. The test fixture values must include `"volumeClaimTemplates":` (for the legacy case) and `"celery":` with `volumeClaimTemplates` (for the new path).
   - `test_worker_sets.py`: The `test_overwrite_volume_claim_templates` test should include a parametrized case exercising the `workers.celery.volumeClaimTemplates` path, with fixture values containing `"celery":` and `volumeClaimTemplates`.

7. **Chart validity**: After changes, `helm lint`, `helm template` (with `CeleryExecutor`), and JSON schema validation of default values against `values.schema.json` must all pass.

## Notes

- The Helm chart uses a `workersMergeValues` helper to merge `celery` section values into `workers`. This merge logic handles the new field automatically.
- When both `workers.volumeClaimTemplates` and `workers.celery.volumeClaimTemplates` are specified, the `celery` path takes precedence.
