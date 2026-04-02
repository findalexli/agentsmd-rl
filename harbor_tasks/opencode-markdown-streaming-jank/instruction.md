# Markdown rendering flashes and jank during streamed assistant responses

## Bug

When the assistant is actively streaming a response, the rendered markdown exhibits two noticeable visual problems:

1. **Flash on each update** — every time new tokens arrive, the entire message container flickers. This is because the browser applies `content-visibility: auto` and `contain-intrinsic-size` to the message wrapper even while the message is still actively growing. Paint containment on a rapidly changing element causes the browser to skip layout, then snap it in — producing a visible flash.

2. **Code blocks become unreadable mid-stream** — when the model is partway through a fenced code block (i.e., the opening triple-backtick has arrived but the closing one hasn't yet), the entire markdown body is re-parsed on every chunk. This causes the code block to lose syntax highlighting and flicker between rendered and raw states. Copy buttons on code blocks also stop working reliably because the DOM elements are fully replaced on each parse.

The root cause is that the markdown renderer in `packages/ui/src/components/markdown.tsx` treats the entire markdown text as a single unit for every parse cycle, with no awareness of whether the response is still streaming. And the message timeline in `packages/app/src/pages/session/message-timeline.tsx` unconditionally applies CSS containment to all messages, including the one currently being written.

## Expected behavior

- While a response is actively streaming, `content-visibility` and `contain-intrinsic-size` should NOT be applied to the active message — only to completed (inactive) messages.
- The markdown renderer should split streaming content so that stable, complete blocks are rendered and cached separately from the in-progress trailing block (e.g., an unclosed code fence). This avoids re-parsing the entire body on each token arrival.
- Copy buttons on code blocks should remain functional during streaming updates.
- When the response is complete (not streaming), the full markdown should render normally as a single unit.

## Relevant code

- `packages/ui/src/components/markdown.tsx` — the `Markdown` component and its rendering pipeline. Currently treats all text as one block with no streaming awareness.
- `packages/ui/src/components/message-part.tsx` — `TextPartDisplay` and `ReasoningPartDisplay` components that render text/reasoning parts. Need to signal streaming state to the markdown renderer.
- `packages/app/src/pages/session/message-timeline.tsx` — applies CSS `content-visibility: auto` and `contain-intrinsic-size` unconditionally via inline styles on every message wrapper.
- `packages/app/src/app.tsx` — provider setup for the markdown renderer.
