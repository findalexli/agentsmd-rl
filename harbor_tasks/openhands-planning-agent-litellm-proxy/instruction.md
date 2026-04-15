# Fix Planning Agent Authentication Error

## Problem

When using the planning agent (sub-conversation feature), authentication errors occur because the LiteLLM proxy key is sent to the wrong endpoint. The base URL resolution fails for certain model name prefixes.

## Symptom Details

- Sub-conversations (planning agents) inherit `llm_model` from the parent conversation
- The SDK transforms model names from `openhands/model` to `litellm_proxy/model` before storage
- When models with the `litellm_proxy/` prefix are processed, the base URL becomes `None` instead of the provider's base URL
- This causes the LiteLLM proxy key to be sent to the wrong endpoint, resulting in authentication failures

## Required Behavior

The base URL resolution logic must correctly handle models with these two prefixes:
- `openhands/` - existing prefix that should continue to work
- `litellm_proxy/` - additional prefix that needs the same base URL handling

For models with either of these prefixes, the base URL resolution should follow this priority:
1. Use the user's explicitly provided base URL (`llm_base_url`) if available
2. Fall back to the provider's configured base URL (`openhands_provider_base_url`) when the user has not provided one
3. Regular models (without either prefix) should continue to use only the user's `llm_base_url`

## Testing Criteria

After the fix:
- Models starting with `litellm_proxy/` should receive the provider's base URL when the user has not specified one
- Models starting with `litellm_proxy/` should use the user's base URL when provided
- Models starting with `openhands/` should continue to work as before
- Regular models should not be affected by the provider's base URL
