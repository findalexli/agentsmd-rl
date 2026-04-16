# Task: Implement Dual-Slot Status Icons for Sidebar

## Problem Description

The Storybook sidebar currently shows status icons for stories, but it cannot display **both** change-detection statuses (new, modified, affected) and test statuses (error, warning, pending, success) simultaneously. When a story has both types of status, only one is shown, which limits visibility into story state.

## What You Need to Do

Implement two new utility functions in `code/core/src/manager/utils/status.tsx` that enable the sidebar to show dual status slots:

### 1. `getChangeDetectionStatus(statuses: StatusByTypeId)`

This function should split the input statuses into two categories based on `typeId`:
- **Change slot**: Statuses where `typeId === CHANGE_DETECTION_STATUS_TYPE_ID` (import from `'storybook/internal/types'`)
- **Test slot**: All other statuses

It should return an object with:
- `changeStatus`: The most critical status value from change-detection statuses (or `'status-value:unknown'` if none)
- `testStatus`: The most critical status value from test statuses (or `'status-value:unknown'` if none)

Use the existing `getMostCriticalStatusValue()` function to determine priority.

### 2. `getGroupDualStatus(collapsedData, allStatuses)`

This function computes dual status for groups and components by aggregating their descendant story statuses.

For each group/component/story in `collapsedData`:
1. Find all descendant leaf stories (type === 'story')
2. Collect all statuses from those stories via `allStatuses`
3. Split into change vs test categories using the same logic as `getChangeDetectionStatus`
4. Return a record mapping item IDs to `{ change: StatusValue, test: StatusValue }`

Use the existing `getDescendantIds()` function from `./tree.ts` to find descendants.

### 3. Export `statusPriority` array

The `Tree.tsx` component needs to use the `statusPriority` array for sorting. Ensure it's exported from `status.tsx`.

## Files to Modify

**Primary file**: `code/core/src/manager/utils/status.tsx`

You'll need to:
1. Add `CHANGE_DETECTION_STATUS_TYPE_ID` to the imports from `'storybook/internal/types'`
2. Add `StatusByTypeId` to the type imports if not already present
3. Implement and export `getChangeDetectionStatus()`
4. Implement and export `getGroupDualStatus()`
5. Ensure `statusPriority` is exported

## Helper Functions Available

- `getMostCriticalStatusValue(statusValues: StatusValue[]): StatusValue` - Already exists, returns most critical status
- `getDescendantIds(collapsedData, itemId, includeItem): string[]` - Import from `'./tree.ts'`
- `CHANGE_DETECTION_STATUS_TYPE_ID` - Import from `'storybook/internal/types'` (value is `'storybook/change-detection'`)

## Status Priority (highest to lowest)

```
'status-value:error' > 'status-value:warning' > 'status-value:new' > 'status-value:modified' > 'status-value:affected' > 'status-value:success' > 'status-value:pending' > 'status-value:unknown'
```

## Validation

Run the repository's checks to validate your changes:

```bash
# From repo root
cd code
yarn test status.test --run

# Type check
cd ..
yarn nx run-many -t check
```

## Hints

1. Look at the existing `getGroupStatus()` function for a pattern on how to traverse `collapsedData` and aggregate statuses
2. The `statusPriority` array already exists at the top of `status.tsx` - just ensure it's exported
3. Use `Object.values()` to iterate over statuses and `filter()` to split by `typeId`
4. For `getGroupDualStatus`, the accumulator should be a `Record<string, { change: StatusValue; test: StatusValue }>`
