# Fix API Key Organization Association in Conversation Creation

## Problem

When creating conversations via API key authentication, the system incorrectly associates conversations with the wrong organization. The `save_app_conversation_info` method in `SaasSQLAppConversationInfoService` (defined in `enterprise/server/utils/saas_app_conversation_info_injector.py`) persists `org_id` based on the user's `current_org_id` field, rather than considering the API key's bound organization.

### Bug Scenario

1. A user creates an API key while viewing "Personal Workspace" (ORG1)
2. The user switches to a different organization (ORG2) in the browser
3. The user uses the API key to create a conversation via `save_app_conversation_info`
4. **Bug**: The conversation's `StoredConversationMetadataSaas` record is saved with `org_id=ORG2` (user's current org) instead of `org_id=ORG1` (API key's org)

### Relevant Code Path

The `SaasSQLAppConversationInfoService` class in `enterprise/server/utils/saas_app_conversation_info_injector.py` has a `save_app_conversation_info` method that creates `StoredConversationMetadataSaas` records. The bug is that when determining the `org_id` for the metadata, the code uses `user.current_org_id` without checking if the user authenticated via an API key that has its own organization binding.

## Requirements

1. **`SaasSQLAppConversationInfoService.save_app_conversation_info`** must use the API key's organization when:
   - The `user_context` has a `user_auth` attribute (indicating API key auth)
   - `user_auth` has a `get_api_key_org_id()` method that returns a non-None UUID

2. **Fallback behavior**: When `get_api_key_org_id()` returns `None` (legacy API keys without org binding) or when the `user_context` does not have `user_auth` (cookie/browser auth), fall back to `user.current_org_id`

3. The `StoredConversationMetadataSaas` record must have the correct `org_id` such that:
   - Conversations created via API key bound to ORG1 appear in ORG1's conversation list
   - Conversations created via API key bound to ORG1 do NOT appear when the user is viewing ORG2
   - `saas_metadata.user_id` and `saas_metadata.org_id` must be correctly set

4. The fix must pass ruff linting, mypy type checking, and pre-commit hooks

5. Existing enterprise tests, storage tests, API key store tests, and server module tests must continue to pass

## Expected Behavior After Fix

| Auth Method | API Key Org Binding | User's current_org_id | Expected org_id in Metadata |
|-------------|---------------------|----------------------|---------------------------|
| API key | ORG1 | ORG2 | ORG1 |
| API key (legacy) | None | ORG1 | ORG1 |
| Cookie/Browser | N/A | ORG1 | ORG1 |

## Implementation Notes

- The `user_context` parameter passed to `SaasSQLAppConversationInfoService` may be a `SpecifyUserContext` (cookie auth) or a `MockAuthUserContext` wrapping a `MockUserAuth` (API key auth)
- `MockUserAuth` has a `get_api_key_org_id()` method that returns the API key's bound org UUID
- `SpecifyUserContext` does NOT have a `user_auth` attribute
- The `StoredConversationMetadataSaas` model has `org_id` and `user_id` fields that must be correctly populated

## Verification

The fix can be verified by:
1. Creating a user with `current_org_id=ORG2`
2. Creating a mock auth context where `api_key_org_id=ORG1`
3. Calling `save_app_conversation_info` to create a conversation
4. Verifying the resulting `StoredConversationMetadataSaas` record has `org_id=ORG1`