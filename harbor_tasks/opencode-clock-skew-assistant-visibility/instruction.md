# Assistant message invisible in web UI under client clock skew

When the client browser's clock is **ahead** of the opencode server's clock,
the first assistant message of a turn disappears from the web UI. The TUI
renders the same session correctly, so the data is on disk — only the web UI
is dropping it.

## What's actually happening

User message IDs are generated client-side using `Date.now()` and the server
reuses those IDs as-is. Assistant message IDs are generated server-side. When
the client clock leads the server by a few seconds, the user message's ID
sorts **after** the first assistant message's ID inside the array of all
session messages. So in the array of messages (sorted by ID) you can end up
with an assistant at index `0` and the user at index `1`, even though the
user spoke first.

A skewed example (3124ms client lead) looks like this when sorted by ID:

```
[0] assistant (parentID = the user below)
[1] user
[2] assistant (parentID = same user)
[3] assistant (parentID = same user)
```

All three assistants belong to that user — their `parentID` field equals the
user message's `id`.

## Expected behaviour

The web UI's per-turn assistant lookup must return **every** assistant whose
`parentID` matches the user message's `id`, regardless of where those
assistants sit in the array. Specifically:

- An assistant whose array index is **less than** the user's index but whose
  `parentID` matches must still be returned.
- An assistant in a later turn (different `parentID`) must NOT be returned.
- A different user message appearing between the queried user and that
  user's own assistants must NOT short-circuit the lookup.
- When the user message's index is `< 0` (not found in the array), return
  the empty result.

The fix lives in `packages/ui/src/components/session-turn.tsx`, inside the
`assistantMessages` memo of the `SessionTurn` component. The memo currently
walks forward only from the user's index and stops at the next message with
`role === "user"` — both of those assumptions break under clock skew. Adjust
the lookup so it relies on `parentID` matching across the whole message
array rather than positional ordering.

## Style

Follow the repository style guide in `AGENTS.md` at the repo root. In
particular:

- Prefer functional array methods (`filter`, `flatMap`, `map`) over imperative
  for-loops where the result is the same.
- Prefer `const` over `let`; reduce variable count by inlining a name that's
  used only once.
- Avoid `else`; prefer early returns.
- Avoid the `any` type; rely on type inference.

## Out of scope

- Changing the server-side ID generation strategy (tracked separately).
- Reverting message filtering or fork/retry handling — leave those flows as
  they are.
