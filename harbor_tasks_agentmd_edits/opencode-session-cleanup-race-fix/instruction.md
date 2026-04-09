# Fix E2E Session Cleanup Race Conditions

The E2E test suite has race conditions during session cleanup. Tests that create temporary sessions or workspaces can fail due to foreign key constraint violations when sessions are deleted while background jobs are still running.

## The Problem

Currently, tests clean up sessions by directly calling `sdk.session.delete()`:

```typescript
await sdk.session.delete({ sessionID }).catch(() => undefined)
```

This can fail when:
1. The session has background jobs still running
2. The session state is not idle
3. Multiple directories (workspaces) reference the same session

## What You Need to Do

### 1. Implement Safe Session Cleanup

Add helper functions to `packages/app/e2e/actions.ts`:

- `waitSessionIdle(sdk, sessionID, timeout?)` - Poll until session status shows idle or doesn't exist
- `stable(sdk, sessionID, timeout?)` - Wait for session metadata to stabilize (no recent updates)
- `cleanupSession({ sessionID, directory?, sdk? })` - Full safe cleanup that:
  - Waits for session to be idle
  - Aborts the session if still busy
  - Waits for stable state after abort
  - Deletes the session

### 2. Update `withSession` helper

Modify the `withSession` function to use `cleanupSession` instead of direct `sdk.session.delete()`.

### 3. Update Fixtures

Update `packages/app/e2e/fixtures.ts`:

- Add `trackSession(sessionID, directory?)` and `trackDirectory(directory)` to the `withProject` fixture
- Update the cleanup logic to use `cleanupSession` for all tracked sessions before cleaning up directories

### 4. Update Documentation

Update `packages/app/e2e/AGENTS.md` to document:
- The new helper functions (`withProject`, `trackSession`, `trackDirectory`)
- The new cleanup pattern using fixture-managed cleanup instead of manual `sdk.session.delete()`
- The recommendation to use `withSession()` and `withProject()` for resource cleanup

## Files to Modify

- `packages/app/e2e/actions.ts` - Add cleanup helpers and update `withSession`
- `packages/app/e2e/fixtures.ts` - Update `withProject` with tracking and safe cleanup
- `packages/app/e2e/AGENTS.md` - Document the new patterns

The AGENTS.md documentation should reflect the actual API you're implementing - include the new helper functions in the "Actions" section and update the "Error Handling" section to recommend fixture-managed cleanup.
