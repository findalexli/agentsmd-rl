# OpenRouter Provider Bug: Tool Support Detection

## Symptom

The OpenRouter provider in `core/llm/toolSupport.ts` has issues with recognizing certain models as tool-supporting:

1. **Gemini 3 models not recognized**: Models like `google/gemini-3-pro-preview` are not detected as supporting tools, even though they should be.

2. **Suffix handling broken**: Models with OpenRouter-specific suffixes like `meta-llama/llama-3.2-3b-instruct:free` fail to match because the `:free` (or `:extended`, `:beta`) suffix is not stripped before pattern matching.

3. **Autocomplete endpoint misconfiguration**: In `CompletionProvider.ts` and `NextEditProvider.ts`, OpenRouter models are incorrectly forced to use the legacy `/completions` endpoint instead of `/chat/completions`.

4. **Gemini thought signatures missing**: When using Gemini models via OpenRouter, tool calls may produce 400 errors because the `thought_signature` field is missing.

## Relevant Files

- `core/llm/toolSupport.ts` - OpenRouter tool support detection logic
- `core/llm/llms/OpenRouter.ts` - OpenRouter LLM class
- `core/autocomplete/CompletionProvider.ts` - Completion provider
- `core/nextEdit/NextEditProvider.ts` - Next edit provider

## Expected Behavior

- `google/gemini-3-pro-preview` should be recognized as a tool-supporting model
- `meta-llama/llama-3.2-3b-instruct:free` should have the `:free` suffix stripped and then match `meta-llama/llama-3.2-3b-instruct`
- OpenRouter should not be forced to use the legacy `/completions` endpoint
- Gemini tool calls via OpenRouter should include `thought_signature` to prevent 400 errors

## Notes

- Tests exist in `core/llm/toolSupport.test.ts` for the `openrouter` provider
- The `PROVIDER_TOOL_SUPPORT` record maps provider names to detection functions