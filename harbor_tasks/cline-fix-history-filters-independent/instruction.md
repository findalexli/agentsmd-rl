# Fix History View Filters: Workspace and Favorites Should Be Independent Toggles

## Problem

In the History view of this VS Code extension, the "Workspace" and "Favorites" filter toggles are mutually exclusive — selecting one deselects the other. This is incorrect behavior: both filters should work as independent toggles that can be active simultaneously.

The Workspace filter is controlled by the `showCurrentWorkspaceOnly` state and the Favorites filter is controlled by the `showFavoritesOnly` state. Currently, these two toggle filters behave as if they're part of a radio button group where only one can be selected at a time, when they should behave like independent checkboxes that can both be active.

## Expected Behavior

- Workspace and Favorites should be independent toggle filters (both can be active at the same time)
- Sort options (Newest, Oldest, Most Relevant) should remain as mutually exclusive radio options
- The Workspace and Favorites filters should be wrapped in a container div that uses both `marginTop` and `flex` CSS properties to maintain visual continuity with the existing layout
- The container div should have a negative top margin to align visually with the radio group above it

## Files to Look At

- `webview-ui/src/components/history/HistoryView.tsx` — contains the filter UI logic with `showCurrentWorkspaceOnly` and `showFavoritesOnly` state

## Documentation Update Requirement

After fixing the code, update `CLAUDE.md`:

- Add a "Miscellaneous" section to `CLAUDE.md`
- Include a tip that `npm run compile` is the correct command (not `npm run build`)
- Mention checking `package.json` for discovering available scripts
