# DeepSeek Reasoner API Parameter Error

When using the `openai-adapters` package to call DeepSeek Reasoner models, API requests fail. DeepSeek's API returns an error when the request includes the `max_tokens` parameter, but the current implementation sends this parameter without conversion.

The issue occurs under either of these conditions:
- The API base URL contains `api.deepseek.com`, OR
- The model name includes `deepseek-reasoner`

Expected behavior:
1. When either condition above is true AND `max_tokens` is provided in the request, the adapter should send `max_completion_tokens` with the same value instead of `max_tokens`, and `max_tokens` should not be present in the final request body
2. When `max_tokens` is not provided, neither `max_tokens` nor `max_completion_tokens` should be added to the request body (no spurious parameters)
3. For other models (like `gpt-4o`) and other API bases, `max_tokens` should continue to be sent unchanged

Note: The codebase already handles a similar parameter conversion for OpenAI's o-series models. The same approach should work for DeepSeek Reasoner models.
