# Fix API Key Organization Association for Conversations

## Problem

In the SaaS/Enterprise edition, conversations created via API key authentication are associated with the wrong organization. When a user creates an API key bound to Organization A, then switches their active organization to Organization B in the web UI, conversations created using that API key are incorrectly saved under Organization B instead of Organization A. This is a data isolation issue.

## Required Fix

The fix must be implemented in the code that handles saving conversation metadata with organization association. The implementation must use these exact patterns:

1. Create a variable named exactly `org_id` that defaults to `user.current_org_id`
2. Check for API key authentication using: `if hasattr(self.user_context, 'user_auth'):`
3. Inside that block, assign exactly: `user_auth = self.user_context.user_auth`
4. Check for the org ID method using: `if hasattr(user_auth, 'get_api_key_org_id'):`
5. Get the API key's org ID using exactly: `api_key_org_id = user_auth.get_api_key_org_id()`
6. Check if it's not None using exactly: `if api_key_org_id is not None:`
7. When not None, assign exactly: `org_id = api_key_org_id`
8. Use `org_id=org_id` when creating the conversation metadata record with organization association

## Required Behavior

The fix must handle three authentication scenarios:

1. **API key with org binding**: When `get_api_key_org_id()` returns a non-None UUID, the conversation's organization must be set to that API key's org ID
2. **Legacy API key (no org binding)**: When `get_api_key_org_id()` returns `None`, fall back to `user.current_org_id`
3. **Cookie/browser auth**: When there's no `user_auth` attribute on the context, use `user.current_org_id` — preserving existing behavior

## Constraints

The modified code must pass ruff linting and formatting per the enterprise config at `enterprise/dev_config/python/ruff.toml`.
