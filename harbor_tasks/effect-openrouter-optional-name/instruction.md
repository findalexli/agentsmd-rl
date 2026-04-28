# Fix: Optional `function.name` in Streaming Tool Call Schema

## The Bug

The `ChatStreamingMessageToolCall` schema in the `@effect/ai-openrouter` package rejects valid streaming tool call chunks from the OpenRouter API.

The OpenAI-compatible streaming spec transmits tool calls across multiple SSE chunks. The `function.name` field is only present on the **first** chunk of a tool call stream; subsequent chunks omit it. However, the schema currently requires `function.name` on every chunk, which causes a `MalformedOutput` / `ParseError` whenever a model returns a tool call in streaming mode.

Compare with the `id` field at the same level — it is already optional, correctly reflecting the SSE spec where certain fields may be absent from individual chunks.

## What Should Happen

A streaming tool call chunk **without** `function.name` (e.g., `{ index: 0, id: null, type: "function", function: { arguments: "..." } }`) must be accepted by the schema and decode successfully, just as chunks missing `id` are accepted today.

## Verification

After the fix, a chunk that omits `function.name` should decode without error. The package should also pass TypeScript type checking (`tsc -b tsconfig.json` from the package directory).

## Code Style Requirements

This project enforces code quality through automated CI checks that must continue to pass:

- `pnpm circular` — verifies no circular dependencies exist
- `pnpm lint` — checks code formatting and style conventions
- `pnpm codegen` — ensures generated code is up to date

Your changes must not introduce violations in any of these checks.

## Constraints

- Do not change the overall structure of the schema class or rename any fields.
- The behavior for chunks that DO include `function.name` must remain unchanged — they must still decode correctly.
