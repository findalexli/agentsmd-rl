# Sessions Changes View - Missing Git Repository Context

In the Agent Sessions window, the Changes view needs to track whether the active session is associated with a Git repository. Currently, there's no context key to indicate when a session lacks a git repository connection.

## Expected Behavior

The Changes view should expose a context key (`sessions.hasGitRepository`) that:
1. Is `true` when the active session has a git repository associated with it
2. Is `false` when the active session has no repository path defined
3. Can be used in menu visibility conditions to show/hide git-dependent actions

Additionally, the "Mark as Done" action (identified as `agentSession.markAsDone`) should appear in the Changes view toolbar with an icon and label visible when appropriate context conditions are met.

## Files to Look At

- `src/vs/sessions/contrib/changes/browser/changesView.ts` - The main Changes view implementation where context keys are defined and bound
- `src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts` - Where session actions like "Mark as Done" are registered

## Context

This is part of the VS Code Agent Sessions feature, which provides a dedicated workbench layer for agentic workflows. The Changes view displays file modifications in a session and its actions should adapt based on session context (e.g., whether the session has a Git repository, whether a PR exists, etc.).

The `vs/sessions` layer sits alongside `vs/workbench` and contains all agent session-specific UI components. See `src/vs/sessions/README.md` and `src/vs/sessions/AGENTS.md` for architectural guidance.
