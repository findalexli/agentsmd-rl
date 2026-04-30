# Task: Update GPT-5.1/5.2 Default Reasoning Effort and Extend Reasoning Effort Types

The `@openai/agents-core` package has default model settings that need updating for newer GPT-5 model variants.

## Symptom

The function `getDefaultModelSettings` in the agents-core package currently returns the same reasoning effort default (`'low'`) for all GPT-5 models. However, the `gpt-5.1` and `gpt-5.2` models should default to reasoning effort `'none'` instead.

## What's Broken

1. Calling `getDefaultModelSettings('gpt-5.1')` returns `reasoning: { effort: 'low' }` — it should return `reasoning: { effort: 'none' }`.

2. Calling `getDefaultModelSettings('gpt-5.2')` returns `reasoning: { effort: 'low' }` — it should return `reasoning: { effort: 'none' }`.

3. The `ModelSettingsReasoningEffort` TypeScript type does not include `'xhigh'` as a valid value. The OpenAI platform now supports `'xhigh'` as a reasoning effort level, so the type must accept it.

## Constraints

- `gpt-5.2-codex` (a variant of gpt-5.2) should still default to `'low'`, not `'none'`. Only the exact models `gpt-5.1` and `gpt-5.2` should get the `'none'` default.

- The `'none'` effort value was already in the `ModelSettingsReasoningEffort` union type (commented as "for gpt-5.1"). This is a type-level annotation — the runtime behavior via `getDefaultModelSettings` must also be updated.

- Update existing comments and documentation strings to reflect the new set of supported reasoning effort values.

## Code Style Requirements

- Run `pnpm eslint` on changed source files and ensure no lint errors.
- Comments must end with a period.
- Add or update unit tests covering the new behavior.
- Follow existing code patterns in the file (e.g., how other GPT-5 model checks are structured).

## Validation

Your changes must pass:
- `pnpm -F agents-core build-check` (TypeScript compilation)
- `pnpm eslint packages/agents-core/src/defaultModel.ts packages/agents-core/src/model.ts` (linting)
- The existing test suite for defaultModel
- New behavioral tests verifying the correct defaults for gpt-5.1, gpt-5.2, and gpt-5.2-codex
