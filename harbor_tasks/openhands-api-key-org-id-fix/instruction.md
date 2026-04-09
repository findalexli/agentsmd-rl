# Fix API Key Organization Association in Conversation Creation

## Problem

When creating conversations via API key authentication, the system incorrectly uses the user's currently selected organization instead of the API key's bound organization. This causes conversations to be associated with the wrong organization.

### Scenario
1. A user creates an API key while viewing "Personal Workspace" (ORG1)
2. The user switches to a different organization (ORG2) in the browser
3. The user uses the API key to create a conversation
4. **Bug**: The conversation is incorrectly saved to ORG2 (user's current org) instead of ORG1 (API key's org)

## Files to Modify

**Primary file**: `enterprise/server/utils/saas_app_conversation_info_injector.py`

Look for the `save_app_conversation_info()` method. The issue is in how the `org_id` is determined when creating SAAS metadata for new conversations.

## Requirements

1. When a user authenticates via API key with an `org_id` binding, the conversation should be associated with that organization
2. For legacy API keys without `org_id`, fall back to the user's `current_org_id`
3. For cookie-based authentication (no API key), continue using the user's `current_org_id`

## Hints

- The `user_context` may have a `user_auth` attribute with a `get_api_key_org_id()` method
- Check if this method exists and returns a non-None value before falling back to `user.current_org_id`
- The relevant code is in the section that creates `StoredConversationMetadataSaas` records

## Expected Behavior

After the fix:
- Conversations created via API key should use the API key's `org_id`
- Conversations created via browser/cookie auth should use the user's `current_org_id`
- The fix should maintain backward compatibility with existing API keys
