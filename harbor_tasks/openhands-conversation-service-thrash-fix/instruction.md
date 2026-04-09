# Fix Sandbox Service Query Thrashing in Conversation Routes

## Problem

The `/config` endpoint in `openhands/server/routes/conversation.py` is making **3 separate queries** to the sandbox service for each request when handling V1 conversations:

1. `_is_v1_conversation()` - calls `get_app_conversation()` to check if it's a V1 conversation
2. `_get_v1_conversation_config()` - calls `get_app_conversation()` again to get the config
3. Inside `_get_v1_conversation_config()`, another call to get the conversation

This causes unnecessary load on the sandbox service (response time 100-200ms per call).

## Goal

Refactor the code to:
1. Use `AppConversationInfoService` instead of `AppConversationService` (the info service is lighter-weight)
2. Make only **1 service call** per request instead of 3
3. Consolidate the two helper functions (`_is_v1_conversation` and `_get_v1_conversation_config`) into a single `_get_v1_conversation_info()` function that returns `AppConversationInfo | None`
4. Return the JSONResponse directly from the main endpoint when V1 conversation info is found

## Key Files

- `openhands/server/routes/conversation.py` - The main file to modify

## Requirements

Your solution should:
1. Replace imports: use `AppConversationInfoService` and `AppConversationInfo` from `openhands.app_server.app_conversation.app_conversation_info_service` and `app_conversation_models`
2. Replace the dependency: use `depends_app_conversation_info_service` instead of `depends_app_conversation_service`
3. Create a new async function `_get_v1_conversation_info()` that:
   - Takes conversation_id and app_conversation_info_service as parameters
   - Returns `AppConversationInfo | None`
   - Handles ValueError/TypeError (invalid UUID) and returns None
   - Handles other exceptions with debug logging and returns None
4. Remove the old helper functions `_is_v1_conversation` and `_get_v1_conversation_config`
5. Update `get_remote_runtime_config()` to:
   - Call `_get_v1_conversation_info()` once
   - If the result is not None, return a JSONResponse with runtime_id and session_id directly
   - Otherwise fall back to the V0 conversation logic

## Testing

The fix should reduce sandbox service response time from 100-200ms to ~6-25ms per request.

Run the unit tests to verify your changes:
```bash
cd /workspace/openhands
poetry run pytest tests/unit/server/routes/test_conversation_routes.py -v
```
