# Task: Fix Planning Agent Authentication Error

## The Problem

The planning agent (sub-conversation) is failing with an authentication error when using certain model name prefixes.

## Root Cause

When the SDK transforms a model name from `openhands/` prefix to a different prefix (such as `litellm_proxy/`), the planning agent fails to authenticate because the `base_url` is not properly set.

## Your Task

1. Locate the file `openhands/app_server/app_conversation/live_status_app_conversation_service.py`
2. Find the method `_configure_llm` in that file
3. Identify where the `base_url` fallback logic is triggered based on model name prefix checks
4. Modify the condition so that models with either prefix receive the correct `base_url`

## Hint

The current code only handles one specific model name prefix. When a model has a different prefix, the `base_url` remains unset, causing the API key to be sent to the wrong endpoint. The fix needs to ensure all relevant prefixes are handled.

## Verification

Run the tests in `tests/unit/app_server/test_live_status_app_conversation_service.py` to verify your fix works correctly.

## Constraints

- Make minimal changes - only modify the necessary condition
- Preserve existing behavior
- Follow the existing code style