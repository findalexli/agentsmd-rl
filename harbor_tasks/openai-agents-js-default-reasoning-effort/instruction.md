# Update default reasoning effort for newer GPT-5 models

The `@openai/agents-core` package ships a small resolver that maps a model
name to default `ModelSettings` (specifically `reasoning.effort` and
`text.verbosity`). The resolver is exposed through two exported functions:

- `gpt5ReasoningSettingsRequired(modelName: string): boolean`
- `getDefaultModelSettings(model?: string): ModelSettings`

Two recently announced model families — **GPT-5.4** (with `mini`, `nano`,
and `pro` variants) and **GPT-5.3-codex** — have specific default
`reasoning.effort` requirements that the current resolver does not handle,
and the existing chat-latest detection only recognises the original
`gpt-5-chat-latest` alias. The resolver currently returns
`{ reasoning: { effort: 'low' }, text: { verbosity: 'low' } }` for any
GPT-5 model that is not in the small `gpt-5.1` / `gpt-5.2` allow-list,
which is wrong for the new families.

Update the resolver so that the following defaults hold for
`getDefaultModelSettings(model)`:

| Model name (and any `-YYYY-MM-DD` snapshot of the same family) | Expected return value |
| --- | --- |
| `gpt-5` | `{ reasoning: { effort: 'low' }, text: { verbosity: 'low' } }` |
| `gpt-5.1` | `{ reasoning: { effort: 'none' }, text: { verbosity: 'low' } }` |
| `gpt-5.2` | `{ reasoning: { effort: 'none' }, text: { verbosity: 'low' } }` |
| `gpt-5.2-codex` | `{ reasoning: { effort: 'low' }, text: { verbosity: 'low' } }` |
| `gpt-5.2-pro` | `{ reasoning: { effort: 'medium' }, text: { verbosity: 'low' } }` |
| `gpt-5.3-codex` | `{ reasoning: { effort: 'none' }, text: { verbosity: 'low' } }` |
| `gpt-5.4` | `{ reasoning: { effort: 'none' }, text: { verbosity: 'low' } }` |
| `gpt-5.4-mini` | `{ reasoning: { effort: 'none' }, text: { verbosity: 'low' } }` |
| `gpt-5.4-nano` | `{ reasoning: { effort: 'none' }, text: { verbosity: 'low' } }` |
| `gpt-5.4-pro` | `{ reasoning: { effort: 'medium' }, text: { verbosity: 'low' } }` |

Snapshots that look like `<family>-YYYY-MM-DD` (for example
`gpt-5.4-2026-03-05`, `gpt-5.4-mini-2026-03-17`,
`gpt-5.4-pro-2026-03-05`, `gpt-5.1-2025-11-13`, `gpt-5-2025-08-07`) must
resolve to the same defaults as their base family.

For other GPT-5 variants whose supported `reasoning.effort` values are
**not** confirmed yet — concretely `gpt-5-mini`, `gpt-5-nano`, and
`gpt-5.1-codex`, including their dated snapshots — `getDefaultModelSettings`
must keep the `text.verbosity = 'low'` default but **omit
`reasoning.effort` entirely**. The returned object must equal exactly
`{ text: { verbosity: 'low' } }`. (At base, these models incorrectly default
to `reasoning.effort = 'low'`.)

The chat-latest detection must also be widened. The following four aliases
are chat-latest aliases and must NOT request reasoning settings:

- `gpt-5-chat-latest`
- `gpt-5.1-chat-latest`
- `gpt-5.2-chat-latest`
- `gpt-5.3-chat-latest`

Concretely, `gpt5ReasoningSettingsRequired` must return `false` for each of
these four names, and `getDefaultModelSettings` must return an empty object
`{}` for each of them.

`gpt5ReasoningSettingsRequired` must continue to return `true` for the
reasoning variants that remained supported, including `gpt-5.2-pro` and
`gpt-5.4-pro`. Models that are not GPT-5 at all (for example `gpt-4o`)
must still return an empty object from `getDefaultModelSettings`.

## Changeset

Any change under `packages/` must be accompanied by a new file under
`.changeset/` describing the change. Use a Conventional Commit-style
summary (for example, `fix: …`) and target the affected package
(`@openai/agents-core`) at the appropriate semver bump (a `patch` is
sufficient for a defaults adjustment).

## Code Style Requirements

- The repository's vitest test suite (`pnpm -F @openai/agents-core exec
  vitest run`) must pass after your change. The existing test suite for
  these two functions has expectations that no longer match the new
  contract (for example, the existing assertion that
  `getDefaultModelSettings('gpt-5-mini')` includes `reasoning.effort:
  'low'`); update those expectations alongside the resolver.
- `pnpm -F @openai/agents-core build-check` (TypeScript `tsc --noEmit`)
  must pass — your changes must compile cleanly.
- `pnpm lint` (ESLint with Prettier defaults) must pass.
- Per `AGENTS.md`, code comments must end with a period.
