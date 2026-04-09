# Fix API Key Organization Association for Conversations

## Problem

When a user creates a conversation via API key authentication in the OpenHands SaaS/Enterprise edition, the conversation is incorrectly associated with the user's currently selected organization (`user.current_org_id`) instead of the organization that the API key is bound to.

This causes a security/isolation issue where:
1. A user creates an API key in Organization A
2. The user switches to Organization B in the web UI (changing their `current_org_id`)
3. When using the API key to create conversations, those conversations are incorrectly saved under Organization B instead of Organization A

## Affected Code

The bug is in `enterprise/server/utils/saas_app_conversation_info_injector.py` in the `save_app_conversation_info()` method.

The current code always uses `user.current_org_id` when creating SAAS metadata for a conversation, ignoring the API key's bound organization.

## Requirements

1. When saving a conversation via API key authentication, the code should check if the `user_context` has a `user_auth` attribute with a `get_api_key_org_id()` method
2. If the API key has an `org_id` binding, use that org_id for the conversation
3. If the API key doesn't have an org_id (legacy key), fall back to `user.current_org_id`
4. For non-API-key auth (browser cookies), the existing behavior should be preserved

## Testing

The fix should handle three scenarios:
1. API key with org_id binding → conversation uses API key's org_id
2. Legacy API key without org_id → conversation uses user's current_org_id
3. Cookie/browser auth → conversation uses user's current_org_id

## Files to Modify

- `enterprise/server/utils/saas_app_conversation_info_injector.py`

The fix requires modifying the `save_app_conversation_info()` method to determine the correct `org_id` before creating the `StoredConversationMetadataSaas` record.
