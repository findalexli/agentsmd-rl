# Bug Report: Submenu group labels shown inline instead of as section headers in Action Widget

## Problem

In VS Code's action widget (used for quick fixes, refactorings, and workspace pickers), when a submenu has grouped actions with labels, the group label is displayed as a description on the first action item in each group rather than as a proper section header. This makes grouped submenus hard to scan — the group name looks like a tooltip or secondary detail instead of visually separating the groups.

This also affects the session workspace picker's browse submenus, where provider labels are passed as the top-level submenu title rather than being associated with the individual action groups, resulting in inconsistent labeling.

## Expected Behavior

Submenu groups that have a label should display that label as a distinct header row above the group's actions, consistent with how top-level action list groups render their headers. Each action's description should reflect its own tooltip, not the group name.

## Actual Behavior

The group label is injected as the `description` of the first action item in each group. Subsequent items in the same group show their tooltip. There are no visual header separators between groups in submenus, making it difficult to distinguish between grouped sections.

## Files to Look At

- `src/vs/platform/actionWidget/browser/actionList.ts`
- `src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts`
