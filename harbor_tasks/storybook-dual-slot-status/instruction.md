# Implement Dual-Slot Status Functionality for Storybook

You are working on Storybook's status management system. The goal is to implement functionality that separates status values into two categories: "change detection" statuses and "test" statuses.

## Background

Storybook's status system tracks statuses by type ID. There is a special type ID `CHANGE_DETECTION_STATUS_TYPE_ID` (imported from `'storybook/internal/types'`) used for change detection statuses. All other type IDs represent test-related statuses.

The file to modify is: `core/src/manager/utils/status.tsx`

## Requirements

### 1. Update Imports

Add imports from `'storybook/internal/types'`:
- `CHANGE_DETECTION_STATUS_TYPE_ID` (constant)
- `StatusByTypeId` (type)
- `StatusesByStoryIdAndTypeId` (type)

### 2. Export `statusPriority`

Export `statusPriority` from `status.tsx` for use by other components like `Tree.tsx`.

### 3. Implement `getChangeDetectionStatus`

Create and export a function named `getChangeDetectionStatus` that separates statuses into two groups:
- Statuses associated with `CHANGE_DETECTION_STATUS_TYPE_ID` are "change" statuses
- All other statuses are "test" statuses
- The function should return an object with `changeStatus` and `testStatus` properties containing the most critical status value from each group

### 4. Implement `getGroupDualStatus`

Create and export a function named `getGroupDualStatus` that:
- Works with entries from `collapsedData` having type `'group'`, `'component'`, or `'story'`
- Aggregates descendant statuses from `allStatuses`
- Separates aggregated statuses into "change" and "test" categories
- Returns a record mapping each entry's ID to an object with `change` and `test` properties

### 5. Preserve Existing Functionality

These existing exports must continue to work:
- `getStatus`
- `getMostCriticalStatusValue`
- `getGroupStatus`
- `StatusByTypeId` type references

## Acceptance Criteria

After implementation:
- `getChangeDetectionStatus` should correctly split statuses into change vs test categories
- `getGroupDualStatus` should compute dual status for groups/components by aggregating their descendants' statuses
- The file should compile without TypeScript errors
- `statusPriority` should be exported for use by Tree.tsx
- `CHANGE_DETECTION_STATUS_TYPE_ID` should be imported and used for filtering
