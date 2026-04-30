# E2E Session Cleanup Race Conditions

## Problem

The e2e test suite in `packages/app/e2e/` has flaky cleanup behavior. When tests finish, sessions are deleted immediately via `sdk.session.delete()` without waiting for them to become idle first. Under CI concurrency, this causes foreign key exceptions and intermittent failures because sessions may still be running when deletion is attempted.

The `withProject` fixture in `fixtures.ts` also doesn't track sessions or workspaces created during tests, so manual cleanup in each test file is error-prone and verbose — some tests forget to clean up, leading to leaked resources.

## Expected Behavior

1. A `cleanupSession` helper should be added to `actions.ts` that properly waits for a session to become idle before deleting it. If the session isn't idle after a short wait, it should be aborted first, then waited for again, then deleted.

2. The `withProject` fixture should gain `trackSession` and `trackDirectory` callbacks so tests can register resources for automatic cleanup during fixture teardown.

3. `withSession` and all spec files should be updated to use the new cleanup mechanism instead of calling `sdk.session.delete()` directly.

4. The project's e2e `AGENTS.md` should be updated to document the new helpers and recommend fixture-managed cleanup over direct session deletion.

## Files to Look At

- `packages/app/e2e/actions.ts` — session action helpers; where cleanupSession and waitSessionIdle should live
- `packages/app/e2e/fixtures.ts` — test fixtures; where trackSession/trackDirectory tracking should be added to withProject
- `packages/app/e2e/AGENTS.md` — e2e testing guide; should document new helpers and updated cleanup patterns
