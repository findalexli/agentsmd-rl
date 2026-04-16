# Ollama /api/show Performance and Robustness Issues

## Problem Description

The Ollama LLM integration in `core/llm/llms/Ollama.ts` has several bugs related to how it fetches and handles model metadata.

## Symptoms

1. **Unnecessary API calls during construction**: When creating Ollama model instances (especially with `AUTODETECT` or when listing many models), the constructor immediately fires `/api/show` HTTP POST requests. This causes a burst of requests even when the model metadata won't be used until later streaming operations begin.

2. **Duplicate requests for same model**: Multiple instances of the same model do not share cached metadata, causing redundant `/api/show` calls.

3. **Crash on regex mismatch**: When parsing the `body.parameters` response from `/api/show`, the code does `if (parts.length < 2)` where `parts` comes from `line.match()`. When the regex doesn't match, `String.match()` returns `null`, causing the code to crash with `TypeError: Cannot read property 'length' of null`.

4. **Explicit options overridden**: When a user explicitly provides `contextLength` in the model options, the value from the `/api/show` response overwrites the user's setting.

## Required Behaviors

The fixed implementation must satisfy all of the following:

1. **Lazy loading**: Model metadata from `/api/show` should only be fetched when actually needed, not during object construction. The fetching should be triggered at the start of streaming operations (the `stream`/`streamChat`/`streamCompletion` methods).

2. **Response caching**: Multiple instances of the same model should reuse cached metadata from a single `/api/show` response promise, avoiding duplicate requests.

3. **AUTODETECT special case**: When the model is the literal string `"AUTODETECT"`, no `/api/show` call should be made. The code should return a resolved promise immediately without making any HTTP requests.

4. **Explicit contextLength preservation**: If the user explicitly provides `contextLength` in the options, that value must be respected and not overwritten by the `num_ctx` value from `/api/show`. The API response should only set `_contextLength` when the user did not provide an explicit value.

5. **Null-safe regex handling**: The code must handle `null` returns from `String.match()` without crashing. When the regex doesn't match, the parsing loop should skip that line gracefully.

## Files to Modify

- `core/llm/llms/Ollama.ts` — The Ollama LLM implementation