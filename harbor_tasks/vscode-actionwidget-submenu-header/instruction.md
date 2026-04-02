# Bug Report: Action Widget Submenu Group Labels Displayed Inline Instead of as Headers

## Problem

In VS Code's action widget, when a submenu contains multiple groups of actions with labels, the group labels are not rendered as proper section headers. Instead, the group label is awkwardly placed as the "description" text of the first action item in each group. This means group labels appear as faded secondary text next to an action rather than as distinct, visually separated section headers above their group.

This is particularly visible in the workspace picker's browse submenu, where provider labels should visually separate groups of browse actions but instead appear cramped alongside the first action entry.

## Expected Behavior

Submenu groups that have labels should display a proper header row above their actions, clearly separating each group visually — consistent with how headers work elsewhere in action lists.

## Actual Behavior

Group labels are concatenated onto the first action item's description field, making them easy to miss and breaking the visual hierarchy of grouped submenu items. Subsequent items in the group show their tooltip (or nothing), but there is no distinct header element.

## Files to Look At

- `src/vs/platform/actionWidget/browser/actionList.ts`
- `src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts`
