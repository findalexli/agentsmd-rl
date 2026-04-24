# OpenRouter Provider Bug: Tool Support Detection

## Symptom

The OpenRouter provider has issues with recognizing certain models as tool-supporting:

1. **Gemini 3 models not recognized**: Models like `google/gemini-3-pro-preview` are not detected as supporting tools, even though they should be.

2. **Suffix handling broken**: Models with OpenRouter-specific suffixes like `meta-llama/llama-3.2-3b-instruct:free` fail to match because the suffix is not stripped before pattern matching.

3. **Autocomplete endpoint misconfiguration**: OpenRouter models are incorrectly forced to use the legacy `/completions` endpoint instead of `/chat/completions`. The condition in `core/autocomplete/CompletionProvider.ts` that forces the legacy endpoint affects OpenAI-based providers including OpenRouter.

4. **Gemini thought signatures missing**: When using Gemini models via OpenRouter, tool calls may produce 400 errors because a required field is missing. The `core/llm/llms/OpenRouter.ts` file handles chat completion modifications.

## Expected Behavior

- `google/gemini-3-pro-preview` should be recognized as a tool-supporting model
- `meta-llama/llama-3.2-3b-instruct:free` should have the `:free` suffix stripped and then match
- OpenRouter should not be forced to use the legacy `/completions` endpoint
- Gemini tool calls via OpenRouter should include the necessary signature field to prevent 400 errors

## Relevant Files

- `core/llm/toolSupport.ts` — handles model tool-support detection for OpenRouter
- `core/autocomplete/CompletionProvider.ts` — determines whether to use legacy completions endpoint
- `core/llm/llms/OpenRouter.ts` — OpenRouter provider implementation with chat body modifications
- `core/nextEdit/NextEditProvider.ts` — also determines whether to use legacy completions endpoint

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
