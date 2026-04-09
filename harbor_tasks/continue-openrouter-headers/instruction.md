# Task: Add OpenRouter Headers to Core LLM Class

## Problem

The Continue project has two OpenRouter implementations:
1. One in `packages/openai-adapters/src/apis/OpenRouter.ts`
2. One in `core/llm/llms/OpenRouter.ts`

The openai-adapters implementation already sends proper OpenRouter headers (`HTTP-Referer`, `X-OpenRouter-Title`, and `X-OpenRouter-Categories`) for marketplace attribution, but the core LLM OpenRouter class does not include these headers in its requests.

Additionally, the openai-adapters implementation currently uses an outdated header name (`X-Title`) instead of the newer `X-OpenRouter-Title`, and is missing the `X-OpenRouter-Categories` header for proper marketplace attribution.

## Requirements

1. Update `packages/openai-adapters/src/apis/OpenRouter.ts`:
   - Change `X-Title` to `X-OpenRouter-Title`
   - Add `X-OpenRouter-Categories: ide-extension` header
   - Export the `OPENROUTER_HEADERS` constant so it can be reused

2. Update `packages/openai-adapters/src/index.ts`:
   - Export `OPENROUTER_HEADERS` from the main package index

3. Update `core/llm/llms/OpenRouter.ts`:
   - Import `OPENROUTER_HEADERS` from `@continuedev/openai-adapters`
   - Modify the constructor to merge these headers into request options
   - Ensure user-configured `requestOptions.headers` can still override these defaults

## Files to Modify

- `core/llm/llms/OpenRouter.ts`
- `packages/openai-adapters/src/apis/OpenRouter.ts`
- `packages/openai-adapters/src/index.ts`

## Notes

- The headers should enable OpenRouter to properly attribute requests to the Continue IDE extension
- User-configured headers should take precedence over the default headers
- The implementation should match the pattern established in the openai-adapters package
