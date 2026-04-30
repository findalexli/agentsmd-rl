# Forward `external_web_access` for the OpenAI web search tool

You are working in the `openai/openai-agents-js` monorepo (TypeScript, pnpm
workspace). The repository is at `/workspace/openai-agents-js`.

The `@openai/agents-openai` package exposes a public helper for configuring
the OpenAI Responses-API `web_search` tool. Locate its API surface and the
hosted-tool → Responses-API converter that turns the helper's output into
the JSON payload sent to the OpenAI API.

## The bug

The OpenAI Responses API web search tool accepts a boolean field
`external_web_access` that controls whether the tool may fetch live
internet content. The Agents SDK does **not** currently forward this
configuration:

1. The public `WebSearchTool` type and its factory function (the helper
   that returns a hosted tool definition for `web_search`) have no option
   to set this value, so callers cannot configure it.
2. Even if a downstream consumer set the underlying internal
   `external_web_access` provider-data field on a hosted tool by hand,
   the converter that turns hosted tools into Responses-API tool payloads
   would drop the value entirely. The converted `web_search` tool
   payload contains `type`, `user_location`, `filters`,
   `search_context_size` — and nothing else.

The result: today there is no way to tell the OpenAI API to disable
external web access for a `web_search` tool from this SDK.

## What to do

Plumb `external_web_access` through the SDK so callers can configure it,
including the explicit value `false`.

Concretely, the public `web_search` factory in the `@openai/agents-openai`
package must accept an option that controls this field, and the
hosted-tool → Responses-API conversion path must forward the value when
(and only when) it has been set by the caller.

### Behavioral requirements

- Calling the public factory with the option set to `true` must produce a
  hosted tool whose internal provider data carries `external_web_access:
  true`. Calling it with the option set to `false` must produce one whose
  internal provider data carries `external_web_access: false` — explicit
  `false` must round-trip and must not be coerced or dropped.
- Calling the public factory **without** the option must leave the
  provider data without an `external_web_access` key at all (so the
  OpenAI API default applies). Do not write `undefined`, do not default
  to `false`.
- The hosted-tool → Responses-API converter for the `web_search` branch
  must include `external_web_access` in the converted tool payload **iff**
  it is present in the source provider data. When it is set to `false`,
  the literal value `false` must appear in the converted payload. When
  the source provider data lacks the field, the converted payload must
  also lack it (no `external_web_access: undefined`).
- The repository's existing test suite for `@openai/agents-openai` must
  continue to pass, and `pnpm -F @openai/agents-openai run build-check`
  (TypeScript `tsc --noEmit` over `src` + `test`) must succeed — the new
  field must be reflected in the type definitions used by the converter,
  not only at runtime.

### API & convention notes

- Public option fields on the exported `WebSearchTool` type are
  camelCase (e.g. `userLocation`, `searchContextSize`); internal
  provider-data and Responses-API fields are snake_case
  (`user_location`, `search_context_size`). Follow the same convention
  for the new option.
- The internal provider-data alias for the web search tool is built as
  `Omit<OpenAI.Responses.WebSearchTool, 'type'> & {...}`. The `openai`
  npm package's typings do not yet expose `external_web_access` on
  `OpenAI.Responses.WebSearchTool`, so you may need to extend the
  internal type (and the converted-payload type at the converter call
  site) to carry the optional `external_web_access?: boolean` field.

### Tests

- Add at least one unit test exercising the new behavior. The
  repository's testing convention is `vitest`; mirror the style of the
  existing tests under `packages/agents-openai/test/`.

### Changeset

- Per the repository's contributor guide, any change under `packages/`
  requires a changeset entry. Add a single `.changeset/*.md` file with a
  Conventional-Commit-styled one-line summary (e.g. `feat: ...`) listing
  the affected package (`@openai/agents-openai`) at the appropriate
  bump level.

## Code Style Requirements

- `pnpm lint` (ESLint) must pass on your changes.
- Public APIs require JSDoc comments.
- Comments end with a period.

## How your work is verified

A test runner will execute `pnpm -F @openai/agents-openai exec vitest`
against fixture tests that exercise the public factory and the
converter directly with both `true` and `false` values, and against the
repository's own test files. It will also run `pnpm -F
@openai/agents-openai run build-check`, `pnpm -F @openai/agents-openai
run build`, and `pnpm lint`.
