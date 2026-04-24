# Ollama /api/show Performance and Robustness Issues

## Problem Description

The Ollama LLM integration in `core/llm/llms/Ollama.ts` has several bugs related to how it fetches and handles model metadata.

## Symptoms

1. **Unnecessary API calls during construction**: When creating Ollama model instances (especially with `AUTODETECT` or when listing many models), the constructor immediately fires `/api/show` HTTP POST requests. This causes a burst of requests even when the model metadata won't be used until later streaming operations begin.

2. **Duplicate requests for same model**: Multiple instances of the same model do not share cached metadata, causing redundant `/api/show` calls.

3. **Crash on regex mismatch**: When parsing the `body.parameters` response from `/api/show`, the code accesses `.length` on a value that comes from `String.match()`. When the regex doesn't match, `match()` returns `null`, causing the code to crash with `TypeError: Cannot read property 'length' of null`.

4. **Explicit options overridden**: When a user explicitly provides `contextLength` in the model options, the value from the `/api/show` response overwrites the user's setting.

## Required Behaviors

The fixed implementation must satisfy all of the following:

1. **Lazy loading**: Model metadata from `/api/show` should only be fetched when actually needed, not during object construction. The fetch should be triggered at the start of streaming operations (the `stream`/`streamChat`/`streamCompletion` methods), via a private method called with `await`.

2. **Response caching**: Multiple instances of the same model should reuse cached metadata from a single `/api/show` response promise. The class should have a private field that stores the cached promise.

3. **AUTODETECT special case**: When the model is the string `"AUTODETECT"`, no `/api/show` call should be made. The code should return early without an API request.

4. **Explicit contextLength preservation**: If the user explicitly provides `contextLength` in the options, that value must be respected and not overwritten by the `num_ctx` value from `/api/show`. A private field should track whether the user provided an explicit value, and the context length should only be set from the API response when no explicit value was provided.

5. **Null-safe regex handling**: The code must safely handle `null` returns from `String.match()` without crashing, before attempting to access properties on the result.

## Files to Modify

- `core/llm/llms/Ollama.ts` — The Ollama LLM implementation

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
