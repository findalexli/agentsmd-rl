# Duplicate reasoning parts in OpenRouter streaming responses

You are working in the [`effect-ts/effect`](https://github.com/Effect-TS/effect) monorepo, checked out at the parent of merge commit `c3e706ff4d01c70ae1754b13c9cbc1f001c09068`. The repository is at `/workspace/effect`. Use `pnpm` (already installed) to run commands.

## The bug

The OpenRouter language-model integration (`@effect/ai-openrouter`) decodes
streamed chat completions into a sequence of `StreamPart` values for the
`@effect/ai` `LanguageModel.streamText` API. Each chunk delta from OpenRouter
may carry **two** fields that describe the model's reasoning trace:

- `reasoning` — a plain string with the reasoning text for that delta.
- `reasoning_details` — a structured array (`reasoning.text`,
  `reasoning.summary`, `reasoning.encrypted` items) carrying the same
  reasoning text, plus richer metadata such as encrypted blobs or
  signatures.

Some OpenRouter providers populate **both** fields on every reasoning delta,
sending the same reasoning text twice — once in `reasoning` and once in the
`reasoning_details[].text` of a `reasoning.text` item. The streaming decoder
currently emits a `reasoning-delta` `StreamPart` for *each* of those fields
independently, so when both are present the consumer of the stream sees every
reasoning token **twice**: once as a plain reasoning delta and once with the
metadata-rich variant. The duplication shows up in the live stream and in the
exported chat history.

When OpenRouter only sends `reasoning` (and not `reasoning_details`), the
plain field must still be emitted exactly once — it is the only reasoning
content available. When OpenRouter only sends `reasoning_details`, only those
items should be emitted. When OpenRouter sends both, exactly the
`reasoning_details` content should be emitted; the plain `reasoning` field is
treated as a fallback for the `reasoning_details`-absent case.

## What to fix

Locate the streaming decoder for the OpenRouter provider in this monorepo and
adjust how reasoning deltas are emitted so that:

1. If a delta has a non-empty `reasoning_details` array, the decoder emits
   reasoning parts derived **only** from `reasoning_details` (one
   `reasoning-delta` per item with non-empty content) and does **not** also
   emit a `reasoning-delta` for the plain `reasoning` field.
2. If `reasoning_details` is absent, `null`, or empty, but `reasoning` is a
   non-empty string, the decoder emits exactly one `reasoning-delta` carrying
   the `reasoning` string.
3. If neither field is present, no reasoning parts are emitted for that delta.
4. Across a multi-chunk stream, the cumulative number of `reasoning-delta`
   parts equals the number of distinct reasoning emissions in the input —
   nothing is duplicated.

The decoder's emission of text deltas, source citations, tool calls, and
finish-reason events must continue to work exactly as before. Do not
restructure surrounding behaviour beyond what the fix requires.

## Code Style Requirements

Run the following from the repository root before submitting; all must pass:

- `pnpm lint packages/ai/openrouter` — ESLint with the project's `dprint`
  formatter rules. Run `pnpm lint-fix packages/ai/openrouter` to autofix
  most issues.
- `cd packages/ai/openrouter && pnpm check` — TypeScript type-checking via
  `tsc -b`.

Follow the existing code style in the file you edit; in particular keep
comments to a minimum and avoid adding new comments that explain *what* the
code is doing.

## Changeset

Per the repository's `AGENTS.md`, every change must be accompanied by a
changeset. Add a new file under `.changeset/` (any unique kebab-case `.md`
filename works) whose body declares a patch-level version bump for
`@effect/ai-openrouter` and briefly describes the user-visible fix. Existing
files in `.changeset/` (besides `README.md` and `config.json`) demonstrate the
expected format.
