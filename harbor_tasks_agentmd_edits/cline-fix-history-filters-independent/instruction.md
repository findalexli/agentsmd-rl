# Fix History View Filters: Workspace and Favorites Should Be Independent Toggles

## Problem

In the History view of this VS Code extension, the "Workspace" and "Favorites" filter toggles are mutually exclusive — selecting one deselects the other. This is a regression: both filters should work as independent toggles that can be active simultaneously.

The root cause is that the Workspace and Favorites toggles are placed inside a `VSCodeRadioGroup` component, which enforces single-selection (radio button) behavior. They need to be moved outside this group.

## Expected Behavior

- Workspace and Favorites should be independent toggle filters (both can be active at the same time)
- Sort options (Newest, Oldest, Most Relevant) should remain as mutually exclusive radio buttons inside `VSCodeRadioGroup`
- The visual appearance should remain consistent — filters should look like they're part of the same group even though they function independently

## Files to Look At

- `webview-ui/src/components/history/HistoryView.tsx` — contains the filter UI logic and JSX layout

## Additional Requirement

After fixing the code, update the relevant documentation to note an important tip about this project: check `package.json` for available scripts before trying to verify builds (e.g., `npm run compile`, not `npm run build`). Add this to the appropriate documentation file in the repository.
