# Bug: Block Row Paste Causes Array Item Duplication in UI

## Symptom

When copying a block row that contains an array field and pasting it into a new block of the same type, the array items appear doubled in the UI. For example, if a block has 3 items in a nested array, pasting the block row results in 6 items showing in the UI. The underlying database data remains correct - this is purely a UI state issue.

## Affected Area

The bug is in the clipboard paste handling logic for blocks with nested arrays, within the `packages/ui/src/elements/ClipboardAction/` directory.

When a block row containing array fields is pasted, the function that merges clipboard data into the form state does not correctly handle ID regeneration for nested array items. During a paste operation, the code must decide which ID entries in the form state path should be preserved from the clipboard data and which should receive newly generated values. The current logic is incorrectly skipping ID regeneration for nested array items that should receive new unique IDs, causing the merged form state to have missing entries for those nested IDs and ultimately leading to duplicate entries appearing in the rendered UI.

## Verification

The test file at `packages/ui/src/elements/ClipboardAction/mergeFormStateFromClipboard.spec.ts` contains tests for the block row paste behavior. Run these tests to verify the fix works correctly. All 8 existing tests should continue to pass after the fix.

## Example Scenario

1. Create a block with a nested array field (e.g., `ctas` array with `buttons` sub-array)
2. Add items to the nested array (e.g., 3 buttons)
3. Copy the block row
4. Paste into a new block of the same type
5. **Expected:** The new block shows the same number of items (3)
6. **Actual (bug):** The new block shows double the items (6)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
