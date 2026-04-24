# Bug: contextLength silently ignored in YAML model config

## Problem

When `contextLength` is set at the model level in `~/.continue/config.yaml`, the value is silently ignored and a default is used instead. The field is stripped during Zod schema parsing because it is not recognized as a valid field at the model level. Users must place `contextLength` inside `defaultCompletionOptions` for it to work, which is unintuitive.

Example config where `contextLength: 65536` is silently dropped:
```yaml
models:
  - name: my-model
    provider: openai
    model: my-model
    contextLength: 65536
    defaultCompletionOptions:
      maxTokens: 32000
```

## Symptoms

Multiple areas of the codebase are affected:

1. **Zod schema strips model-level contextLength**: The Zod schema that validates model configuration (in `packages/config-yaml/src/schemas/models.ts`) defines a `baseModelFields` variable that determines which fields are accepted at the model level. Currently `contextLength` is not recognized at the model level and is silently removed. The schema must accept `contextLength` as a valid model-level field (just as it accepts other optional fields like `apiKey` and `apiBase`).

2. **Validation ignores model-level contextLength**: Config validation in `packages/config-yaml/src/validation.ts` warns when max tokens are too close to context length, but only reads context length from `defaultCompletionOptions`, ignoring model-level values. The validation must compute an "effective" context length value that prefers the model-level `contextLength` over `defaultCompletionOptions.contextLength`. The computed variable should be named `effectiveContextLength`. The validation warning must use these effective values in its message.

3. **GUI uses wrong fallback constant**: The context-length selector (`selectSelectedChatModelContextLength`) in `gui/src/redux/slices/configSlice.ts` falls back to `DEFAULT_MAX_TOKENS` (4096) when no context length is explicitly configured, but it should use `DEFAULT_CONTEXT_LENGTH` (32768) instead. Context length and max tokens are distinct concepts with different default values.

4. **Core config ignores model-level contextLength**: The module `core/config/yaml/models.ts` that converts YAML model definitions into runtime configuration objects reads `contextLength` only from `defaultCompletionOptions.contextLength`, not from the model level. The code must fall back from `model.defaultCompletionOptions.contextLength` to `model.contextLength` when constructing `llmOptions`.

## Notes

- This affects only YAML config; JSON config may behave differently.
- Some users work around this by placing `contextLength` inside `defaultCompletionOptions`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
