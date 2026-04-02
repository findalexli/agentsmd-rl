# Bug Report: Session list item height not updating correctly after dynamic content change

## Problem

In the VS Code Sessions view, when a session item's content changes dynamically (e.g., expanding an approval request or updating session details), the tree view fails to recalculate the correct row height. Instead of reflecting the new height based on the item's current state, the tree row remains at an incorrect size, causing content to be clipped or leaving excess whitespace.

## Expected Behavior

When a session item's rendered height changes (for example, when an approval model updates or content expands), the tree should recalculate and apply the correct height for that specific item, matching what the delegate would compute for its current state.

## Actual Behavior

The tree view attempts to update the element height but does not provide the correct computed value. This results in rows that are visually mismatched — content may overflow or be cut off, and the list can appear broken after interactive state changes within session items.

## Files to Look At

- `src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts`
