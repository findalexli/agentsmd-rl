# Bug: Missing subagent session footer and style guide violations

## Context

The opencode TUI has a concept of "subagent sessions" — child sessions spawned by a parent session. When viewing a subagent session, users need navigation controls to move between the parent session and sibling subagent sessions, along with token usage and cost information.

## Problem

1. **Missing subagent footer**: When a user opens a subagent session (a session with a `parentID`), there is no footer component displayed. Users have to rely solely on keyboard shortcuts to navigate between parent and child sessions, with no visual indication of available navigation or session cost/usage.

   A new component file `packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx` must be created that exports a `SubagentFooter` component.

2. **Style guide violations in dialog components**:
   - `packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx`: When the variant list is empty after model selection, the dialog state does not behave correctly — it should clear but does not.
   - `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx`: Contains a lint error (unused import) that must be removed.

## Expected Behavior

- A new file `subagent-footer.tsx` in the session directory exports `SubagentFooter` component that:
  - Displays "Subagent session" as the title
  - Shows token usage (input, output, reasoning, cache read/write) and cost information
  - Provides navigation buttons: Parent, Prev/Previous, Next with keyboard shortcut hints
  - Uses mouse event handlers (onMouseUp/onClick/onMouseDown/onPress) for interactivity
  - Only appears when the session has a `parentID` (conditionally rendered)
- The session index (`packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`) imports and renders the `SubagentFooter` component when `parentID` is present
- `dialog-model.tsx` control flow is corrected so that when a model is selected and the variant list is empty, the dialog clears properly
- `dialog-variant.tsx` has no unused imports (lint-clean)

## Files to Investigate

- `packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx` (new file to create)
- `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`
- `packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx`
- `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx`