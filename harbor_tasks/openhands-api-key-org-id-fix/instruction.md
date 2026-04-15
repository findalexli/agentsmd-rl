# Fix API Key Organization Association in Conversation Creation

## Problem

When creating conversations via API key authentication, the system incorrectly associates conversations with the wrong organization. The conversation metadata persists the organization ID based on the user's currently selected organization in the browser, rather than considering which organization the API key belongs to.

### Scenario

1. A user creates an API key while viewing "Personal Workspace" (ORG1)
2. The user switches to a different organization (ORG2) in the browser
3. The user uses the API key to create a conversation
4. **Bug**: The conversation is incorrectly saved to ORG2 (user's current org) instead of ORG1 (API key's org)

## Requirements

1. When a user authenticates via API key and the API key has an organization binding, the conversation's SAAS metadata should be associated with the API key's organization
2. For legacy API keys without an organization binding, fall back to the user's `current_org_id`
3. For cookie-based authentication (no API key), continue using the user's `current_org_id`
4. The fix must pass ruff linting, mypy type checking, and pre-commit hooks
5. Existing enterprise tests, storage tests, API key store tests, and server module tests must continue to pass

## Expected Behavior

After the fix:
- Conversations created via API key should be associated with the API key's bound organization
- Conversations created via browser/cookie auth should use the user's `current_org_id`
- Cross-org visibility must be correct: conversations created via API key bound to ORG1 should not appear when the user is viewing ORG2
- The fix should maintain backward compatibility with existing API keys that have no org binding
