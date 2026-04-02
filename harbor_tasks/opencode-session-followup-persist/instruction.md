# Bug: Queued followups lost when switching projects

## Summary

In the OpenCode app, users can queue followup messages during an active session. However, the followup queue is lost whenever the user switches to a different project and then switches back. All previously queued followups—including any that were paused or had failed—disappear entirely.

## Affected file

`packages/app/src/pages/session.tsx`

## Reproduction

1. Open a session and queue several followup messages
2. Switch to a different project
3. Switch back to the original project
4. Observe that the followup queue is empty — all queued items are gone

## Expected behavior

The followup queue should survive project switches. When the user returns to the original project, their queued followups (including paused and failed entries) should still be present.

## Context

The app already has a persistence utility (`packages/app/src/utils/persist.ts`) that can scope stored data to a workspace directory. Other parts of the session page use this persistence layer, but the followup queue state is currently kept only in component memory.

## Hints

- Look at how the followup store is initialized and consider what happens to its state across component re-mounts
- The `Persist` module provides workspace-scoped storage that ties data to a specific project directory
- The `persisted` wrapper can be applied to an existing SolidJS store to add persistence
