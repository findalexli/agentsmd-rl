# Table rowSelection Crash with preserveSelectedRowKeys

## Problem

The Table component crashes when using row selection with `preserveSelectedRowKeys` enabled. The crash occurs when the `selectedRowKeys` prop transitions from an array value to `undefined`, and code attempts to iterate over the now-undefined selection keys.

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

## Expected Behavior

The Table should handle the transition from `selectedRowKeys: []` to `selectedRowKeys: undefined` gracefully when `preserveSelectedRowKeys` is enabled, without crashing. All array operations on the selected keys must receive a valid array, never `undefined`.

## Files to Modify

- `components/table/hooks/useSelection.tsx`

## Implementation Notes

The file contains an `EMPTY_LIST` constant that provides a safe empty array reference. Ensure that any code that calls array methods on the selected keys is always working with a valid array. Consider what happens when `mergedSelectedKeys` becomes `undefined` during the `updatePreserveRecordsCache` effect and `derivedSelectedKeys` computation.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
