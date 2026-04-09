# Fix Table rowSelection Crash When selectedRowKeys Becomes undefined

## Problem

The `Table` component crashes when `rowSelection.selectedRowKeys` transitions from an array value to `undefined` while `preserveSelectedRowKeys` is enabled.

## Symptom

When using the Table component with rowSelection:
1. Start with `rowSelection={{ selectedRowKeys: ['someKey'] }}`
2. Update to `rowSelection={{ selectedRowKeys: [] }}`
3. Then update to `rowSelection={{ preserveSelectedRowKeys: true }}` (without selectedRowKeys defined)

A runtime error occurs: `TypeError: Cannot read property 'forEach' of undefined`

## Location

The issue is in the `useSelection` hook which handles row selection logic for the Table component.

**File to modify:** `components/table/hooks/useSelection.tsx`

## Root Cause

The hook uses `mergedSelectedKeys` directly in several places including:
- The `updatePreserveRecordsCache` effect
- The `derivedSelectedKeys` calculation via `conductCheck`

When `selectedRowKeys` becomes `undefined`, `mergedSelectedKeys` can be `undefined`, but the code expects an array and calls `.forEach()` on it, causing the crash.

## Expected Fix

Ensure `mergedSelectedKeys` is always treated as an array by coalescing `undefined` to an empty array (`[]`) before using it. The variable `EMPTY_LIST` (already defined in the file as `[]`) can be used as the fallback.

Key areas to fix:
1. Create a coalesced version of `mergedSelectedKeys` (e.g., `mergedSelectedKeys ?? EMPTY_LIST`)
2. Use this coalesced version in all places that expect an array:
   - The `updatePreserveRecordsCache` call in the effect
   - The `conductCheck` function call
   - The `checkStrictly` return value
3. Update the effect dependency array to include all used dependencies

## Testing

The fix should be verified by:
1. Running TypeScript compilation to ensure no syntax errors
2. Running the existing Table.rowSelection tests
3. Ensuring the specific scenario (selectedRowKeys from `[]` to `undefined` with `preserveSelectedRowKeys: true`) no longer crashes

## Context

This is a bug fix for issue #57416. The Table component is a core component used extensively, so the fix should maintain backward compatibility and not change the external API.
