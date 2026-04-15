# Fix Sandbox Service Query Thrashing in Conversation Routes

## Problem

The `/config` endpoint in `openhands/server/routes/conversation.py` is making **3 separate queries** to the sandbox service for each request when handling V1 conversations. This causes unnecessary load on the sandbox service (response time 100-200ms per call).

## Goal

Refactor the code so that only **1 service call** is made per request instead of 3. The endpoint should still correctly handle both V1 and V0 conversations.

## Hint

The refactoring should:
- Use a lighter-weight service variant for conversation info lookup
- Consolidate the separate helper functions into a single helper
- Return the response directly in the V1 branch without additional service calls

## Testing

The fix should reduce sandbox service response time from 100-200ms to ~6-25ms per request.

Run the unit tests to verify your changes:
```bash
cd /workspace/openhands
poetry run pytest tests/unit/server/routes/test_conversation_routes.py -v
```