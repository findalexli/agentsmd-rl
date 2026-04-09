# Fix Return Type on DbtProjectComponent._get_dbt_event_iterator

## Problem

When customizing `DbtProjectComponent`, having the broad type of `Iterator` instead of `DbtEventIterator` on `DbtProjectComponent._get_dbt_event_iterator()` causes type-linting errors if you try to use `iterator.with_insights()` in your `DbtProjectComponent.execute()` method.

The issue is that `Iterator` is too generic - it doesn't expose the specific methods like `with_insights()`, `fetch_row_counts()`, and `fetch_column_metadata()` that are available on `DbtEventIterator`.

## What Needs to Change

### 1. Update `DbtProjectComponent._get_dbt_event_iterator()`

**File:** `python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py`

The method currently returns `Iterator` but should return `DbtEventIterator[DbtDagsterEventType]`.

You'll also need to add the necessary imports:
- `DbtDagsterEventType` from `dagster_dbt.core.dbt_event_iterator`
- `DbtEventIterator` from `dagster_dbt.core.dbt_event_iterator`

### 2. Update return types in `DbtEventIterator`

**File:** `python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py`

Three methods have redundant long union type annotations that should be simplified to use the existing `DbtDagsterEventType` alias:

- `fetch_row_counts()` - currently returns the full union, should return `DbtEventIterator[DbtDagsterEventType]`
- `fetch_column_metadata()` - currently returns the full union, should return `DbtEventIterator[DbtDagsterEventType]`
- `with_insights()` - currently returns the full union, should return `DbtEventIterator[DbtDagsterEventType]`

## Files to Modify

1. `python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py`
2. `python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py`

## Relevant Types

The `DbtDagsterEventType` alias is already defined in `dbt_event_iterator.py` as:
```python
DbtDagsterEventType: TypeAlias = (
    Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation
)
```

You should use this alias consistently instead of the full union type.
