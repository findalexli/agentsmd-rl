# Bug: Queued followups lost when switching projects

## Summary

In the OpenCode app, users can queue followup messages during an active session. However, the followup queue is lost whenever the user switches to a different project and then switches back. All previously queued followups—including any that were paused or had failed—disappear entirely.

## Reproduction

1. Open a session and queue several followup messages
2. Switch to a different project
3. Switch back to the original project
4. Observe that the followup queue is empty — all queued items are gone

## Expected behavior

The followup queue should survive project switches. When the user returns to the original project, their queued followups (including paused and failed entries) should still be present.

## File to modify

The fix must be implemented in `packages/app/src/pages/session.tsx`. The page function must remain exported as `export default function Page`.

## Technical requirements

The fix must satisfy all of the following:

1. **Followup store fields**: The followup store must retain its core fields: `items`, `failed`, `paused`, and `edit`.

2. **Store implementation**: The followup state must use SolidJS's `createStore` (not `createSignal`).

3. **Persistence layer**: The followup store must be wrapped with a persistence layer using imports from a module whose name contains "persist" (e.g., `@/utils/persist`).

4. **Workspace scoping**: The persistence must be scoped per-project using the `.workspace()` API (or equivalent workspace/directory-based scoping using `sdk.directory`), not global. Without this, followups would still be lost on project switch.

5. **No `any` type**: The followup persistence block must not use TypeScript's `any` type (neither `as any` nor `: any` annotations).

6. **No try/catch, else, or for loops** in the followup persistence block. Use functional array methods instead of for loops, prefer early returns over else statements, and avoid try/catch where possible.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
