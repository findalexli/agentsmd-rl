# VS Code Sessions: Cannot Open Archived Sessions

## Problem

When a user clicks on an archived session in the sessions panel, the session view briefly flickers open and then immediately returns to the new session screen. The only workaround is to unarchive the session first, which is inconvenient when users just want to preview archived content.

## Expected Behavior

Clicking on an archived session should open it for viewing without immediately bouncing back to the new session view.

## Relevant Code

The issue is in `src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts`. Look at:

- The `setActiveSession` method
- The `_onSessionsChanged` handler
- How the session archive state (`isArchived`) is being observed and reacted to

## Hints

- The problem involves how the code reacts when a session is found to be archived
- Consider when `openNewSessionView()` is being called and why it might be triggered incorrectly
- The reactive observable pattern (`IObservable`, `observableValue`, etc.) is central to this code
- Look for logic that monitors archive state changes and triggers view transitions
