# Streaming markdown renders broken formatting while response is still arriving

## Bug

When the AI assistant is streaming a response, partially-arrived markdown is rendered with broken inline formatting. Specifically:

1. **Unclosed emphasis markers** — if the model has sent `hello **world` but hasn't yet sent the closing `**`, the raw asterisks appear in the output instead of rendering bold text. The same happens for inline code backticks (`` ` ``).

2. **Half-formed links** — a partially streamed link like `[docs](https://example.com/gu` turns into broken clickable markup (a mangled anchor tag) instead of showing the link text as plain text until the URL is complete.

The existing streaming logic in `packages/ui/src/components/markdown.tsx` already handles one edge case (splitting open code fences from stable content so they can be highlighted incrementally), but it does **not** heal any other incomplete inline markdown before passing it to `marked.parse()`.

## Where to look

- `packages/ui/src/components/markdown.tsx` — the `blocks()` helper (around line 81) is the streaming pre-processor. It currently only checks for open code fences and doesn't touch inline emphasis or links at all.

## Expected behavior

While a response is still streaming:

- Unclosed emphasis (`**`, `*`, `__`, `_`, `` ` ``) should be temporarily closed so the text renders as styled instead of showing raw marker characters.
- Incomplete links should appear as plain text (not clickable) until the full `[text](url)` syntax is present.
- The existing code-fence splitting behavior must be preserved.
- Once streaming is complete, the final markdown should render normally with no temporary healing applied.
