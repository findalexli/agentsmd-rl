# Fix History View Filters: Workspace and Favorites Should Be Independent Toggles

## Problem

In the History view of this VS Code extension, the "Workspace" and "Favorites" filter toggles are mutually exclusive with the sort options — selecting one deselects all others. This is incorrect behavior: the Workspace and Favorites filters should work as independent toggles that can be active simultaneously, while only the sort options (Newest, Oldest, Most Relevant) remain mutually exclusive.

The Workspace filter is controlled by `showCurrentWorkspaceOnly` state and the Favorites filter is controlled by `showFavoritesOnly` state. Currently both filter types behave like radio buttons when the filters should be checkboxes.

## Expected Behavior

- Workspace and Favorites filters must be independent toggle filters (both can be active at the same time)
- Sort options (Newest, Oldest, Most Relevant) must remain as mutually exclusive radio options within VSCodeRadioGroup
- The HistoryView.tsx file must have at least 5 `<VSCodeRadio` elements
- After the fix, the file should contain a flex container div with both `marginTop` and `flex` properties, using a negative top margin to align the filter controls
- Both `showCurrentWorkspaceOnly` and `showFavoritesOnly` filter controls must appear after the closing `</VSCodeRadioGroup>` tag

## Visual Alignment Issue

The filter controls currently appear misaligned relative to the sort options above them. The fix must address this visual alignment using a flex container with negative top margin while allowing the filters to function as independent toggles.

## Files to Look At

- `webview-ui/src/components/history/HistoryView.tsx` — contains the filter UI logic
- `package.json` — for discovering available scripts

## Documentation Update Requirement

After fixing the code, update `CLAUDE.md`:

- Add a "Miscellaneous" section
- Include a tip about checking `package.json` for available scripts
- Mention that `npm run compile` is the correct build command (not `npm run build`)