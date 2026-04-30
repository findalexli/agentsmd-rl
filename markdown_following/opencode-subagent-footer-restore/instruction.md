# Bug: Missing subagent session footer and style guide violations

## Context

The opencode TUI has a concept of "subagent sessions" — child sessions spawned by a parent session. When viewing a subagent session, users need navigation controls to move between the parent session and sibling subagent sessions, along with token usage and cost information.

## Problem

### 1. Missing subagent footer component

When a user opens a subagent session (a session with a `parentID`), there is no footer component displayed. Users have to rely solely on keyboard shortcuts to navigate between parent and child sessions, with no visual indication of available navigation or session cost/usage.

The session index file at `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx` currently has a `<box height={1} />` element that should be removed and replaced with a proper subagent navigation component.

### 2. Style guide violations in dialog components

Two dialog components in `packages/opencode/src/cli/cmd/tui/component/` have issues that cause lint or build failures:
- `dialog-model.tsx`: When a user selects a model in the provider/model selection dialog, and that model has no variants available, the dialog does not close as expected
- `dialog-variant.tsx`: Contains an imported symbol that is not used anywhere in the file

## Expected Behavior

### Subagent footer component

Create a new component file `packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx` that exports a `SubagentFooter` component with the following characteristics:

**Content:**
- Displays the text "Subagent session" as a title
- Shows token usage information including input tokens, output tokens, reasoning tokens, and cache read/write counts
- Shows cost information in USD using currency formatting
- Displays three navigation controls: one to go to the Parent session, one for Previous/Prev subagent, one for Next subagent

**Implementation requirements:**
- The component must access token data via a `.cache` property (e.g., `tokens.cache.read`, `tokens.cache.write`)
- For number formatting (token counts, cost), the component must use either `Intl.NumberFormat` with a locale (e.g., `"en-US"`), or a `Locale` utility that produces localized number strings
- The component must use mouse event handlers for interactivity: at least one of `onMouseUp`, `onClick`, `onMouseDown`, or `onPress` must be present on the navigation controls
- The component must not use `any` type, `try/catch`, `for` loops, or `let` declarations (per project style guidelines)
- The component must use functional array methods (`.reduce`, `.map`, `.filter`, `.find`, `.findLast`, etc.) rather than imperative loops

**Integration:**
- The session index (`packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`) must import `SubagentFooter` from `./subagent-footer.tsx`
- The `SubagentFooter` component must be conditionally rendered only when the session has a `parentID` — wrap it in a `<Show when={session()?.parentID}>` block

### Dialog model selection fix

In `packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx`, when a user selects a model that has no variants available, the dialog should close (clear). Currently, the dialog remains open in this scenario. The fix must not use an `else` block — restructure the control flow so that when the variant list is empty, the dialog clears without wrapping it in an else branch.

### Dialog variant cleanup

In `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx`, remove any import statement that imports a symbol that is never used in the file. The file currently has an import from `@tui/context/sync` that should be removed if `useSync` is not referenced in the component body.

## Files to investigate

- `packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx` (new file to create)
- `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`
- `packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx`
- `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx`

## Verification

After applying changes:
- `dialog-model.tsx` and `dialog-variant.tsx` must pass prettier formatting checks
- All modified TSX files must have balanced braces
- The repo must pass typecheck (`bun run typecheck`) and unit tests (`bun test`)
- The SubagentFooter component must be imported and rendered in the session index, conditional on `parentID`
- No `else` blocks may remain in `dialog-model.tsx` or the new `subagent-footer.tsx`