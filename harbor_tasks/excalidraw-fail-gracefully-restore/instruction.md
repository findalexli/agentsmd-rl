# Fix Error Handling in Restore

## Problem

The `restoreElements` function in `packages/excalidraw/data/restore.ts` crashes when:
1. An arrow binding repair throws an error
2. An element restoration throws an error

This prevents the entire scene from loading if any single element is corrupted or has invalid data.

## Task

Modify the `restore.ts` file to handle errors gracefully:

1. **Arrow binding repair**: The `repairBinding` function should catch errors during binding repair and return `null` instead of crashing

2. **Element restoration**: The `restoreElements` function should catch errors during individual element restoration and skip that element instead of crashing the entire restore process

## Requirements

- When an error occurs during arrow binding repair, it should be caught and the binding should be stripped (return `null`)
- When an error occurs during element restoration, it should be caught and that element should be filtered out
- Errors must be logged to the console with contextual information (e.g., "Error repairing binding:" or "Error restoring element:")
- The restore process should continue and return the successfully restored elements
- All existing tests should continue to pass

## Files to Modify

- `packages/excalidraw/data/restore.ts` - Add error handling to `repairBinding` and `restoreElements`

## Testing

Run the test suite to verify your fix:
```bash
yarn test:update
```

Or run just the restore tests:
```bash
yarn vitest run restore
```
