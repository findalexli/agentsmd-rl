# Move session context info into prompt footer

The TUI currently shows session metadata (token usage, context percentage, and cost) in a dedicated `Header` component rendered above the message scroll area in the session view. This wastes vertical screen space and creates visual clutter—the information is useful but doesn't justify its own layout row.

## What needs to change

1. **Remove the standalone session header** (`packages/opencode/src/cli/cmd/tui/routes/session/header.tsx`) — delete the file entirely and all references to it.

2. **Surface token usage and cost in the prompt footer** (`packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx`) — when a session has assistant messages with token data, compute the context usage (total tokens, percentage of model limit) and cumulative cost, then display them in the prompt footer's bottom bar. When there's no usage data, fall back to showing the existing variant/agent hotkey hints.

3. **Clean up the session route** (`packages/opencode/src/cli/cmd/tui/routes/session/index.tsx`) — remove the `Header` import, the `showHeader` toggle state, the command palette entry for toggling the header, and the `<Header />` render call.

4. **Make the variant cycle command visible** (`packages/opencode/src/cli/cmd/tui/app.tsx`) — the `variant.cycle` command is currently suppressed from the command palette. It should be visible alongside other agent commands.

## Relevant files

- `packages/opencode/src/cli/cmd/tui/routes/session/header.tsx` — the component to remove
- `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx` — session route that renders the header
- `packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx` — prompt component that should absorb the context display
- `packages/opencode/src/cli/cmd/tui/app.tsx` — command registry

## Notes

- Format cost as USD currency and token counts with locale-appropriate number formatting.
- The usage display should show context percentage only when the model has a known context limit.
- When there's no usage data to display, fall back to the existing variant/agent keybind hints.
