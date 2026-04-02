# Bug Report: Changes View action bar styles broken in modal editor and diff stats not hiding correctly

## Problem

The Changes View in VS Code has two issues. First, the CSS selectors for the action bar visibility (show on hover/focus/select) and the diff stats hiding behavior use `.changes-view-body` as their parent selector. This selector is too narrow — it only matches when the list is rendered inside the Changes View pane body, but the same list component is also rendered in other contexts (e.g., the modal editor). In those contexts, the action bar never appears on hover and diff stat counts never hide when the toolbar is visible.

Second, when a user clicks on a file entry in the Changes View and there is only a single item in the list, the file opens in a modal/embedded diff editor unnecessarily. The modal navigation mode is always forced on regardless of how many items exist, which is disorienting when there's only one file — the user expects a simple editor open, not a multi-file navigation experience.

## Expected Behavior

Action bar buttons should appear on hover/focus/select in all contexts where the editing session list is rendered. Single-item lists should open files directly without modal navigation.

## Actual Behavior

Action bars are invisible on hover in non-pane contexts. Single file entries still open with modal multi-file navigation enabled.

## Files to Look At

- `src/vs/sessions/contrib/changes/browser/changesView.ts`
- `src/vs/sessions/contrib/changes/browser/media/changesView.css`
