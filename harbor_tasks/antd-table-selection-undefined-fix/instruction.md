# Fix Table rowSelection Crash with Undefined selectedRowKeys

## Problem

The Ant Design Table component crashes with a runtime error when:
1. `rowSelection.selectedRowKeys` is initially set to `[]` (empty array)
2. Later changed to `undefined`
3. `preserveSelectedRowKeys` is enabled

The crash occurs because `mergedSelectedKeys` becomes `undefined` and subsequent code tries to iterate over it using `forEach` or pass it to functions expecting an array.

## Expected Behavior

The Table must not crash when `selectedRowKeys` transitions from `[]` to `undefined` while `preserveSelectedRowKeys` is enabled. The component should handle this transition gracefully.

## What to Fix

The fix must ensure the selection state is always treated as an array even when the underlying value is `undefined`. Specifically, introduce a local constant (e.g., `mergedSelectedKeyList`) that holds `mergedSelectedKeys ?? EMPTY_LIST` and use it in place of raw `mergedSelectedKeys` throughout the hook. The regression tests that validate this fix are:
- "works with preserveSelectedRowKeys after receive selectedRowKeys from [] to undefined"
- "works with selectionType radio receive selectedRowKeys from [] to undefined"
- "cache with preserveSelectedRowKeys" (Table rowSelection test)

## Verification

Run the Table rowSelection tests:
```bash
npm test -- Table.rowSelection.test.tsx --testNamePattern "preserveSelectedRowKeys"
```

All linting checks must pass:
```bash
npm run lint:script -- components/table/
npm run lint:biome
npm run lint:md
npm run lint:changelog
```

TypeScript compilation must succeed:
```bash
npx tsc --noEmit
```

## Related Issue

- Issue #57416: Table rowSelection crashes when selectedRowKeys becomes undefined