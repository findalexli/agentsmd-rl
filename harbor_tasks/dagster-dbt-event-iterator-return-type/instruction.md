## Problem

When working with `DbtProjectComponent` subclasses, type checkers cannot properly infer the available methods on the iterator returned by `_get_dbt_event_iterator()`. The current return type annotation is too broad (using `Iterator` without type parameters), which prevents proper type inference for methods like `.with_insights()`, `.fetch_row_counts()`, and `.fetch_column_metadata()` when used in subclasses.

Additionally, within the iterator class itself, return type annotations are inconsistent - they repeat a verbose union type across multiple methods instead of using a centralized type alias, making the code harder to maintain.

## Symptoms

1. Subclasses of `DbtProjectComponent` that call `_get_dbt_event_iterator()` cannot access iterator-specific methods with proper type completion.
2. The iterator methods `fetch_row_counts()`, `fetch_column_metadata()`, and `with_insights()` each declare return types using a long, repeated union instead of a shared type alias.

## Required Fix

Your solution must meet the following requirements (verified by the test suite):

1. **Type Alias Definition**: Create a type alias named exactly `DbtDagsterEventType` using `TypeAlias`. This alias must include the union of all event types in this order:
   - `Output`
   - `AssetMaterialization`
   - `AssetCheckResult`
   - `AssetObservation`
   - `AssetCheckEvaluation`

2. **Import Pattern**: The component file must import both types using this exact import statement:
   ```python
   from dagster_dbt.core.dbt_event_iterator import DbtDagsterEventType, DbtEventIterator
   ```

3. **Component Return Type**: The `_get_dbt_event_iterator()` method must have its return type changed from `Iterator` to `DbtEventIterator[DbtDagsterEventType]`.

4. **Iterator Method Return Types**: The methods `fetch_row_counts()`, `fetch_column_metadata()`, and `with_insights()` must return the forward reference string `"DbtEventIterator[DbtDagsterEventType]"` (with the quotes, as a forward reference).

5. **Consistency**: There must be at least 3 occurrences of the pattern `"DbtEventIterator[DbtDagsterEventType]"` in the iterator file to ensure consistency across all related methods.

## Files to Modify

You will need to modify two files within the `dagster-dbt` library:
- A file containing the class `DbtProjectComponent` and its method `_get_dbt_event_iterator`
- A file containing the class `DbtEventIterator` with methods `fetch_row_counts`, `fetch_column_metadata`, and `with_insights`

## Verification

Your fix should:
1. Allow proper type inference when calling `_get_dbt_event_iterator()` in subclasses
2. Use a centralized type alias instead of repeating union types
3. Pass type checking without errors
4. Include all five event types in the type alias: `Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation`
