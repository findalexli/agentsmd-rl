# Fix Type Annotation for DbtProjectComponent._get_dbt_event_iterator

## Problem

When implementing a custom `DbtProjectComponent.execute()` method, developers try to use methods like `iterator.with_insights()`, `iterator.fetch_row_counts()`, or `iterator.fetch_column_metadata()` on the iterator returned by `_get_dbt_event_iterator()`. However, type checkers report that these methods do not exist on the current return type.

The `_get_dbt_event_iterator()` method in `DbtProjectComponent` has a return type annotation of `Iterator` (from `collections.abc`). This generic type doesn't expose the dagster-specific methods that `DbtEventIterator` provides.

## Expected Behavior

Code like the following should pass type checking:

```python
def execute(self, context) -> Iterator[DbtDagsterEventType]:
    iterator = self._get_dbt_event_iterator(context)
    enriched = iterator.with_insights()  # should type-check
    counts = iterator.fetch_row_counts()  # should type-check
    metadata = iterator.fetch_column_metadata()  # should type-check
```

## Files to Examine

1. `python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py` - Contains `DbtProjectComponent` class and its `_get_dbt_event_iterator()` method
2. `python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py` - Contains `DbtEventIterator` class with methods `with_insights()`, `fetch_row_counts()`, `fetch_column_metadata()`, and the `DbtDagsterEventType` type alias

## Verification

After fixing, the following checks should pass:
- `ruff check` passes on both files
- Python syntax is valid (`py_compile`)
- The `_get_dbt_event_iterator()` return type annotation in `component.py` uses `DbtEventIterator` with `DbtDagsterEventType` as the type parameter
- The `fetch_row_counts()`, `fetch_column_metadata()`, and `with_insights()` methods in `dbt_event_iterator.py` use `DbtEventIterator[DbtDagsterEventType]` as their return type (not the long union type)
- The `DbtDagsterEventType` type alias is properly defined as a `TypeAlias` in `dbt_event_iterator.py`