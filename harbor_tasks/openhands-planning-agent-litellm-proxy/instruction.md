# Fix Planning Agent Authentication Error

## Problem

When using the planning agent (sub-conversation feature) with the OpenHands provider, authentication errors occur. The planning agent fails to connect to the LLM endpoint.

## Root Cause

The `_configure_llm` method in `openhands/app_server/app_conversation/live_status_app_conversation_service.py` only checks for the `openhands/` prefix to determine if it should use the provider's base URL:

```python
if model and model.startswith('openhands/'):
    base_url = user.llm_base_url or self.openhands_provider_base_url
```

However, when a sub-conversation (planning agent) inherits `llm_model` from the parent conversation, the SDK has already transformed the model name from `openhands/model` to `litellm_proxy/model` before storage. The current code doesn't recognize the `litellm_proxy/` prefix, so the sub-conversation gets `base_url=None`, causing the LiteLLM proxy key to be sent to the wrong endpoint.

## Your Task

Fix the `_configure_llm` method to also check for the `litellm_proxy/` prefix, in addition to the existing `openhands/` check. This ensures that sub-conversations inherited from the SDK-transformed model name correctly receive the provider's base URL.

## Key Details

- The fix should be minimal - just add the `litellm_proxy/` prefix check alongside `openhands/`
- User's explicit `llm_base_url` should still be preferred when provided
- Regular models (not starting with either prefix) should continue to use `user.llm_base_url` only

## Files to Modify

- `openhands/app_server/app_conversation/live_status_app_conversation_service.py` - Add `litellm_proxy/` prefix check in `_configure_llm`
