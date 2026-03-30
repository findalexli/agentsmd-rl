# Fix: DataFrame NaN values becoming 0 after sorting

## Problem

When a `gr.DataFrame` with `datatype=["number", "number"]` contains NaN values and the user sorts the table, the NaN values silently become 0. This is a data corruption bug that changes cell values without any user action beyond sorting.

## Root Cause

The `cast_value_to_type` function in `js/dataframe/shared/utils/utils.ts` does not handle `null` or `undefined` values before attempting type coercion. When a NaN value from pandas is serialized as JSON `null`, the function proceeds to call `Number(null)` which returns `0`, and `isNaN(0)` is `false`, so the value is returned as `0` instead of being preserved as `null`.

The data flow is: pandas NaN -> JSON null -> `cast_value_to_type(null, "number")` -> `Number(null)` = `0` -> sent back as 0 instead of null.

## Expected Fix

The `cast_value_to_type` function should preserve `null` and `undefined` values for all data types, returning them as-is before any type coercion logic runs.

## Files to Investigate

- `js/dataframe/shared/utils/utils.ts` -- the `cast_value_to_type` function
