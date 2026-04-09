# Fix DataFrame Group Flicker

## Problem

The DataFrame component flickers when scrolling through grouped rows. The CSS styling uses `tr:nth-child(even)` and `tr:nth-child(odd)` selectors to apply alternating row backgrounds. These selectors conflict with virtual scrolling because DOM nodes get recycled — the `:nth-child` position changes as rows enter/leave the viewport, causing visual flickering.

The issue is visible in `js/dataframe/shared/Table.svelte`, `js/dataframe/shared/VirtualTable.svelte`, and `js/dataframe/shared/RowNumber.svelte`.

## Expected Behavior

Row striping should use explicit class-based selectors instead of `nth-child` pseudo-selectors. A base `tr` rule should set the even-row background, and a `tr.row-odd` selector should set the odd-row background. The `nth-child` rules must be removed from all dataframe components.

## Config/Documentation Updates

After fixing the code, update the project documentation to reflect current tooling versions and setup instructions:

1. **CONTRIBUTING.md** — The pnpm version prerequisite is outdated and needs to match the current required version. The browser test section should also document the full dependency installation steps, including which pip requirements files and Playwright browsers are needed.

2. **js/README.md** — The CI browser test instructions should be updated to match the complete setup process, including all required Python dependencies and both Chromium and Firefox browsers.

## Files to Look At

- `js/dataframe/shared/Table.svelte` — main table component with row styling
- `js/dataframe/shared/VirtualTable.svelte` — virtual scroll table with nth-child override
- `js/dataframe/shared/RowNumber.svelte` — row number column with nth-child background rules
- `CONTRIBUTING.md` — project contribution guide
- `js/README.md` — frontend development documentation
