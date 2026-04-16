# Table rowSelection Crash with preserveSelectedRowKeys

## Problem

The Table component crashes when using row selection with `preserveSelectedRowKeys` enabled. The crash occurs when `mergedSelectedKeys` becomes `undefined` and code attempts to call `.forEach()` on it in `components/table/hooks/useSelection.tsx`.

## Reproduction Steps

1. Render a Table with `rowSelection` prop containing `selectedRowKeys` set to an array (e.g., `['Jack']`)
2. Re-render the Table with `selectedRowKeys` set to an empty array `[]`
3. Re-render again with `preserveSelectedRowKeys: true` but **without** the `selectedRowKeys` prop (making it `undefined`)
4. Try to interact with row selection (e.g., click a checkbox)

## Error

The component throws a runtime error:
```
TypeError: Cannot read properties of undefined (reading 'forEach')
```

## Files to Modify

- `components/table/hooks/useSelection.tsx`

## Required Fix

The file contains an `EMPTY_LIST` constant that provides a safe empty array reference. You must introduce a new variable named `mergedSelectedKeyList` that ensures `mergedSelectedKeys` is always an array before being passed to functions that call array methods on it.

Specifically:

1. Create a variable named exactly `mergedSelectedKeyList` using the nullish coalescing operator with `EMPTY_LIST` as the fallback when `mergedSelectedKeys` is undefined

2. The `updatePreserveRecordsCache()` function call in the useEffect must use `mergedSelectedKeyList` instead of `mergedSelectedKeys`

3. The useEffect dependency array must include `mergedSelectedKeyList` and `updatePreserveRecordsCache`

4. The `derivedSelectedKeys` useMemo must use `mergedSelectedKeyList` instead of `mergedSelectedKeys || []`

5. The `conductCheck()` function call must receive `mergedSelectedKeyList` instead of `mergedSelectedKeys`

6. The useMemo dependency array must include `mergedSelectedKeyList` instead of `mergedSelectedKeys`

## Expected Behavior

The Table should handle the transition from `selectedRowKeys: []` to `selectedRowKeys: undefined` gracefully when `preserveSelectedRowKeys` is enabled, without crashing. All array operations on the selected keys must receive a valid array, never `undefined`.
