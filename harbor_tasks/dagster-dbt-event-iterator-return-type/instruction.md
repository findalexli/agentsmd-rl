## Problem

When working with `DbtProjectComponent` subclasses, type checkers cannot properly infer the available methods on the iterator returned by `_get_dbt_event_iterator()`. The current return type annotation is too broad, which prevents proper type inference for methods like `.with_insights()`, `.fetch_row_counts()`, and `.fetch_column_metadata()` when used in subclasses.

Additionally, within the iterator class itself, return type annotations are inconsistent - they repeat a verbose union type across multiple methods instead of using a centralized type alias, making the code harder to maintain.

## Symptoms

1. Subclasses of `DbtProjectComponent` that call `_get_dbt_event_iterator()` cannot access iterator-specific methods with proper type completion.
2. The iterator methods `fetch_row_counts()`, `fetch_column_metadata()`, and `with_insights()` each declare return types using a long, repeated union instead of a shared type alias.

## Required Fix

Your solution must meet the following requirements (verified by the test suite):

1. **Type Alias Definition**: Create a type alias (using `TypeAlias`) in the iterator file that centralizes the union of event types. The type alias should be used consistently across all iterator methods.

2. **Import Pattern**: The component file must import the necessary types from `dagster_dbt.core.dbt_event_iterator` to use the iterator and its associated type alias.

3. **Component Return Type**: The `_get_dbt_event_iterator()` method must have a return type that enables proper type inference for iterator-specific methods in subclasses.

4. **Iterator Method Return Types**: The methods `fetch_row_counts()`, `fetch_column_metadata()`, and `with_insights()` should return a type that uses the centralized type alias.

5. **Consistency**: The iterator methods should use the centralized type alias consistently across all related methods.

## Files to Modify

You will need to modify two files within the `dagster-dbt` library:
- A file containing the class `DbtProjectComponent` and its method `_get_dbt_event_iterator`
- A file containing the class `DbtEventIterator` with methods `fetch_row_counts`, `fetch_column_metadata`, and `with_insights`

The type alias must include all of these event types: `Output`, `AssetMaterialization`, `AssetCheckResult`, `AssetObservation`, `AssetCheckEvaluation`.

## Verification

Your fix should:
1. Allow proper type inference when calling `_get_dbt_event_iterator()` in subclasses
2. Use a centralized type alias instead of repeating union types
3. Pass type checking without errors

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `pyright (Python type checker)`
