# Sessions Changes View - Missing Git Repository Context

In the Agent Sessions window, the Changes view and Code Review actions need to know whether the active session is associated with a Git repository. Currently, there is no context key to indicate this.

## Expected Behavior

1. A new `sessions.hasGitRepository` context key should be defined and bound in the Changes view, reflecting whether the active session's repository observable is defined.
2. The Code Review action in the Changes toolbar should only appear when the session has a git repository — its `when` clause needs the `sessions.hasGitRepository` condition.

## Files to Look At

- `src/vs/sessions/contrib/changes/browser/changesView.ts` — The main Changes view implementation where context keys are defined and bound
- `src/vs/sessions/contrib/codeReview/browser/codeReview.contributions.ts` — Where the code review action is registered with menu visibility conditions

## Context

This is part of the VS Code Agent Sessions feature, which provides a dedicated workbench layer for agentic workflows. The Changes view displays file modifications in a session and its actions should adapt based on session context (e.g., whether the session has a Git repository, whether a PR exists, etc.).

The `vs/sessions` layer sits alongside `vs/workbench` and contains all agent session-specific UI components. See `src/vs/sessions/README.md` and `.github/skills/sessions/SKILL.md` for architectural guidance.
