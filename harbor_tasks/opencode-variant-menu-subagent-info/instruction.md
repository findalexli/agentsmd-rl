# Subagent navigation and display issues in TUI

## Problem

Several usability issues exist in the TUI's subagent and session workflows:

### 1. Subagent cycling direction is inverted

In `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`, the `cycleSession` function moves in the wrong direction when the user requests "next" or "previous" subagent. Pressing the "next" keybind actually goes to the *previous* session and vice versa.

### 2. Subagent footer lacks type and index information

In `packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx`, the footer just displays a static "Subagent session" label with no indication of:
- What *type* of subagent it is (e.g. "Coder", "Explorer")
- Which subagent you are viewing out of how many (e.g. "2 of 5")

The subagent type can be extracted from the session title (which contains patterns like `@coder subagent`). The index can be computed from sibling sessions with the same parent.

### 3. Task descriptions lack subagent type context

In the `Task` component in `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`, the task description just shows "Task {description}" with no indication of which subagent type spawned the task.

## Expected behavior

1. Navigation direction should match user intent — "next" goes forward, "previous" goes backward
2. The subagent footer should display the agent type and position (e.g. "Coder (2 of 5)")
3. Task descriptions should include the subagent type (e.g. "Coder Task — description")

## Relevant files

- `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx` — session cycling logic, Task component
- `packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx` — subagent footer display

## Hints

- Look at how `direction` is applied in `cycleSession` — the arithmetic sign matters
- The session object has a `title` field and a `parentID` — these are the keys to computing subagent info
- Check for dead code (unused imports, unreferenced components) that should be cleaned up
