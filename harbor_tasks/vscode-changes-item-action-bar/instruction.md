# Bug Report: Changes view item action bar overlaps diff stats even when toolbar has no actions

## Problem

In the Changes view (sessions/changes), the diff stats (line count badges showing additions/deletions) on each file row are unconditionally hidden whenever a row is hovered, focused, or selected. This is intended to make room for the action toolbar that appears on interaction — but the toolbar is not always visible. In certain version modes, the toolbar has no actions to display, yet the diff stats still disappear on hover/focus/select, leaving an empty gap where useful information used to be.

Additionally, the `ChangesTreeRenderer` does not have access to the current version mode context, so context-key-dependent menu contributions that control toolbar visibility cannot react to version mode changes. This means the toolbar's action bar doesn't correctly reflect whether actions should be shown for the current mode.

## Expected Behavior

When the action toolbar has no actions to display, the diff stats (line counts) should remain visible on hover, focus, and selection. The toolbar visibility context should accurately reflect the current version mode.

## Actual Behavior

Diff stats are always hidden on hover/focus/select regardless of whether the toolbar actually contains any actions, causing a confusing empty space.

## Files to Look At

- `src/vs/sessions/contrib/changes/browser/changesView.ts`
- `src/vs/sessions/contrib/changes/browser/media/changesView.css`
