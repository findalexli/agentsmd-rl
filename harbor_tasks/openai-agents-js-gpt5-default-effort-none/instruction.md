# Update default model settings and reasoning-effort typing

You are working in the **openai-agents-js** monorepo (a pnpm workspace).
Repository root: `/workspace/openai-agents-js`. The package you will be
modifying is `@openai/agents-core`, located at
`packages/agents-core/`.

## Background

The package exports two helpers (in `@openai/agents-core`) that need to stay
consistent:

- `getDefaultModelSettings(model?: string): ModelSettings` — returns the
  default `reasoning` and `text` settings for a given model name. For
  `gpt-5*` family models it currently returns
  `{ reasoning: { effort: 'low' }, text: { verbosity: 'low' } }`.
- `gpt5ReasoningSettingsRequired(modelName: string): boolean` — returns
  `true` for any model whose name starts with `gpt-5` except
  `gpt-5-chat-latest`.

The `ModelSettingsReasoningEffort` type alias enumerates the currently
supported reasoning-effort values used by the `effort` field of
`ModelSettingsReasoning`.

## What is broken / missing

1. **Defaults for the newest GPT-5 family members are wrong.** For
   `gpt-5.1` and `gpt-5.2`, the default reasoning effort returned by
   `getDefaultModelSettings` should be **`'none'`** (with `text.verbosity`
   still set to `'low'`). It is currently `'low'`.

   Concretely, after your change:

   ```ts
   getDefaultModelSettings('gpt-5.1')
   // => { reasoning: { effort: 'none' }, text: { verbosity: 'low' } }

   getDefaultModelSettings('gpt-5.2')
   // => { reasoning: { effort: 'none' }, text: { verbosity: 'low' } }
   ```

   **Other `gpt-5*` models must keep their existing defaults** of
   `{ reasoning: { effort: 'low' }, text: { verbosity: 'low' } }`. In
   particular:

   - `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, and `gpt-5-pro` continue to use
     `effort: 'low'`.
   - `gpt-5.2-codex` (a codex variant) continues to use
     `effort: 'low'` — only the bare `gpt-5.1` / `gpt-5.2` model names get
     the new `'none'` default.

   Non `gpt-5*` models (e.g. `gpt-4o`) must keep returning `{}` (an empty
   `ModelSettings`).

2. **`gpt5ReasoningSettingsRequired` already covers dotted variants**
   because it uses a `startsWith('gpt-5')` check, so calling it with
   `'gpt-5.1'`, `'gpt-5.2'`, or `'gpt-5.2-codex'` should return `true`.
   Make sure the unit-test coverage for these dotted names exists.

3. **`ModelSettingsReasoningEffort` is missing a value.** Add the literal
   string `'xhigh'` as a member of the `ModelSettingsReasoningEffort` union
   in `packages/agents-core/src/model.ts`, alongside the existing
   `'none' | 'minimal' | 'low' | 'medium' | 'high' | null` members. After
   your change, the following must type-check:

   ```ts
   import type { ModelSettingsReasoningEffort } from '@openai/agents-core';
   const a: ModelSettingsReasoningEffort = 'xhigh';
   const b: ModelSettingsReasoningEffort = 'none';
   ```

   The accompanying TSDoc that lists the currently supported effort values
   in both `ModelSettingsReasoningEffort` and the `effort` field of
   `ModelSettingsReasoning` should continue to enumerate the supported
   literals.

## Acceptance criteria

- `getDefaultModelSettings` returns `effort: 'none'` for `gpt-5.1` and
  `gpt-5.2` (with `text.verbosity` still `'low'`); all other `gpt-5*`
  variants — including `gpt-5.2-codex` — still return `effort: 'low'`.
- `getDefaultModelSettings('gpt-4o')` still returns `{}`.
- `'xhigh'` is a valid `ModelSettingsReasoningEffort`.
- The package's existing tests at
  `packages/agents-core/test/defaultModel.test.ts` continue to pass, and
  the new behavior is covered by new test cases.
- `pnpm -F @openai/agents-core build-check` succeeds.
- The change is accompanied by a `.changeset/*.md` file declaring an
  appropriate bump for `@openai/agents-core`.

## Code Style Requirements

- TypeScript only — match the existing code style in the package.
- Follow the repository's ESLint and Prettier configs (`eslint.config.mjs`,
  default Prettier).
- **Comments must end with a period** (this is enforced by the repo's
  contributor guide).
- Public API additions/changes must keep their JSDoc/TSDoc up to date.
