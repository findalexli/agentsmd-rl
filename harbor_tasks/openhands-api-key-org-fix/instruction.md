# Fix API Key Organization Association for Conversations

## Problem

In the OpenHands SaaS/Enterprise edition, conversations created via API key authentication are associated with the wrong organization. The bug manifests as follows:

1. A user creates an API key bound to Organization A
2. The user switches their active organization to Organization B in the web UI (changing their `current_org_id`)
3. When using the API key to create conversations, those conversations are incorrectly saved under Organization B instead of Organization A

This is a data isolation issue — conversations end up in the wrong organization's scope.

## Root Cause

The code that creates `StoredConversationMetadataSaas` records always uses `user.current_org_id` as the org association, regardless of whether the request was authenticated via an API key that carries its own org binding.

## Codebase Context

The enterprise edition has a conversation metadata service (`SaasSQLAppConversationInfoService`) with an async method `save_app_conversation_info()` that creates and stores `StoredConversationMetadataSaas` entries. The service is registered via `SaasAppConversationInfoServiceInjector`.

The authentication context available in this method provides:
- `self.user_context` — the authenticated user's context. When API key auth is used, this object has a `user_auth` attribute. For cookie/browser auth, this attribute is absent.
- When `user_auth` is present, it may expose `get_api_key_org_id()` which returns the UUID of the org bound to the API key, or `None` for legacy keys without org binding.

## Requirements

Fix the `save_app_conversation_info()` method so that:

1. **API key with org binding**: The conversation's `StoredConversationMetadataSaas` org_id should come from the API key's bound organization
2. **Legacy API key (no org binding, `get_api_key_org_id()` returns `None`)**: Fall back to `user.current_org_id`
3. **Cookie/browser auth (no `user_auth` attribute on context)**: Use `user.current_org_id` — preserving existing behavior

The `StoredConversationMetadataSaas` creation must use the correctly determined org_id rather than directly referencing `user.current_org_id`.

The modified code must pass ruff linting and formatting per the enterprise config at `enterprise/dev_config/python/ruff.toml`.
