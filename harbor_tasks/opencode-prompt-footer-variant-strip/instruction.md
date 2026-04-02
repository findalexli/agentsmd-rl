# Remove unused variant cycle hint from prompt footer

## Context

The TUI prompt component (`packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx`) renders a footer bar with keyboard shortcut hints. Among these hints, there is a "variants" shortcut displayed via the `variant_cycle` keybind when variant models are available.

## Problem

The variant cycle display in the prompt footer is dead UI — the feature it advertises is unused and adds visual noise to the footer. When the user has not yet interacted with a session (i.e., the `usage()` accessor returns falsy and `store.mode === "normal"`), the footer currently shows:

1. A "variants" hint (conditioned on `local.model.variant.list().length > 0`)
2. An "agents" hint
3. A "commands" hint

The "variants" hint should be removed entirely. The "agents" and "commands" hints should remain.

## Scope

Look at the footer rendering logic inside the `<Match when={true}>` block (the default/fallback match within the `<Switch>` for `store.mode === "normal"`). The `<Show>` block that conditionally renders the variant cycle keybind text should be removed.

## Expected outcome

- The prompt footer no longer displays the variant cycle shortcut hint
- The agent cycle and command list hints remain unchanged
- No other footer behavior is affected
