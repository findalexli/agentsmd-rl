# Fix Table rowSelection Crash with Undefined selectedRowKeys

## Problem

The Ant Design Table component crashes with a runtime error when:
1. `rowSelection.selectedRowKeys` is initially set to `[]` (empty array)
2. Later changed to `undefined`
3. `preserveSelectedRowKeys` is enabled

The crash occurs because `mergedSelectedKeys` becomes `undefined` and subsequent code tries to iterate over it using `forEach` or pass it to functions expecting an array.

## Where to Look

Focus on `components/table/hooks/useSelection.tsx`. This hook manages the selection state and is where the crash originates.

Look for:
- The `mergedSelectedKeys` variable that comes from `useMergedState`
- How `mergedSelectedKeys` is used in `useEffect` for `updatePreserveRecordsCache`
- How `mergedSelectedKeys` is used in `useMemo` for `derivedSelectedKeys`

## Expected Fix

The fix should ensure that `mergedSelectedKeys` is always treated as an array even when it's `undefined`. A clean approach is to create a fallback variable using the nullish coalescing operator.

The fix should:
1. Add a fallback: `const mergedSelectedKeyList = mergedSelectedKeys ?? EMPTY_LIST;`
2. Use `mergedSelectedKeyList` instead of `mergedSelectedKeys` in:
   - The `useEffect` that calls `updatePreserveRecordsCache`
   - The `useMemo` that computes `derivedSelectedKeys`
3. Update dependency arrays to use the new variable

## What You Should NOT Do

- Don't add runtime checks at every usage site (clutters the code)
- Don't modify the test file (tests are already provided)
- Don't change the public API or prop types
- Don't use `|| []` instead of `?? EMPTY_LIST` (could cause issues with falsy values)

## Verification

The test file at `components/table/__tests__/Table.rowSelection.test.tsx` already includes a regression test that covers this scenario. Run the specific test:

```bash
npm test -- Table.rowSelection.test.tsx --testNamePattern "works with preserveSelectedRowKeys after receive selectedRowKeys from \[\] to undefined"
```

The test should pass after your fix.

## Related Issue

- Issue #57416: Table rowSelection crashes when selectedRowKeys becomes undefined
