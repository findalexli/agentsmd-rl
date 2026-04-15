# Fix Return Type on DbtProjectComponent._get_dbt_event_iterator

## Problem

When customizing `DbtProjectComponent`, having the broad type of `Iterator` instead of `DbtEventIterator` on `DbtProjectComponent._get_dbt_event_iterator()` causes type-linting errors if you try to use `iterator.with_insights()` in your `DbtProjectComponent.execute()` method.

The issue is that `Iterator` is too generic - it doesn't expose the specific methods like `with_insights()`, `fetch_row_counts()`, and `fetch_column_metadata()` that are available on `DbtEventIterator`.

## Files

The relevant files are in `python_modules/libraries/dagster-dbt/dagster_dbt/`:

1. `components/dbt_project/component.py` - Contains `DbtProjectComponent` class with `_get_dbt_event_iterator()` method
2. `core/dbt_event_iterator.py` - Contains `DbtEventIterator` class and `DbtDagsterEventType` alias

## Requirements

The following return type annotations must be changed:

1. `DbtProjectComponent._get_dbt_event_iterator()` should return `DbtEventIterator[DbtDagsterEventType]` instead of `Iterator`

2. The following methods in `DbtEventIterator` currently return a verbose union type `DbtEventIterator[Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation]` and should be simplified to return `DbtEventIterator[DbtDagsterEventType]`:
   - `fetch_row_counts()`
   - `fetch_column_metadata()`
   - `with_insights()`

## Relevant Types

The `DbtDagsterEventType` alias is already defined in `dbt_event_iterator.py` as:

```python
DbtDagsterEventType: TypeAlias = (
    Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation
)
```

This alias should be used consistently for the return type annotations instead of spelling out the full union. The necessary types (`DbtEventIterator`, `DbtDagsterEventType`) can be imported from `dagster_dbt.core.dbt_event_iterator`.
