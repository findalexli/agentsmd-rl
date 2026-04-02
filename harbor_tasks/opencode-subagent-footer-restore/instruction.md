# Bug: Missing subagent session footer and style guide violations

## Context

The opencode TUI has a concept of "subagent sessions" — child sessions spawned by a parent session. When viewing a subagent session, users need navigation controls to move between the parent session and sibling subagent sessions, along with token usage and cost information.

## Problem

1. **Missing subagent footer**: When a user opens a subagent session (a session with a `parentID`), there is no footer component displayed. Users have to rely solely on keyboard shortcuts to navigate between parent and child sessions, with no visual indication of available navigation or session cost/usage.

   The session view in `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx` does not render any footer for subagent sessions.

2. **Style guide violations in dialog components**:
   - `packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx`: The `onSelect` handler uses an `else` block instead of the project's preferred early-return pattern (see the repo's style guide on control flow).
   - `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx`: Contains an unused import that should be removed.

## Expected Behavior

- When viewing a subagent session, a footer should appear showing:
  - A "Subagent session" title
  - Token usage and cost information
  - Navigation buttons (Parent, Prev, Next) with their keyboard shortcut hints
- The footer should only appear for sessions that have a `parentID`
- Dialog components should follow the project style guide (no `else` blocks, no unused imports)

## Files to Investigate

- `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`
- `packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx`
- `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx`
