# Sync IsWorkspaceGroupCappedContext Key in Sessions View

The Sessions View (`src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts`) has an `IsWorkspaceGroupCappedContext` context key that controls UI behavior (e.g., showing/hiding actions) based on whether the workspace group is at its session capacity limit. However, this context key is never bound or synchronized with the actual persisted state.

This means:
1. The context key always has its default value, regardless of the actual workspace group state
2. The "Reset Filters" action doesn't reset this context key
3. UI elements conditioned on this key show incorrect state

Fix by:
- Adding a `workspaceGroupCappedContextKey: IContextKey<boolean>` field to SessionsView
- Binding it with `IsWorkspaceGroupCappedContext.bindTo(contextKeyService)` in the constructor
- Syncing it with `sessionsControl.isWorkspaceGroupCapped()` in renderBody
- Resetting it in the filter reset action
