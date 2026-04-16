# Route Linear Resolver Conversations to Claimed Org Workspaces

## Problem

The Linear resolver currently creates all conversations in users' personal workspaces, even when the repository belongs to an organization that has claimed the corresponding Git organization in OpenHands. This breaks the expected behavior where conversations for claimed repos should be created in the organization's workspace for better collaboration and visibility.

When a repository belongs to a claimed organization and the user is a member of that org, conversations should be routed to the organization's workspace. When the repository is not part of a claimed org or the user is not a member, conversations should fall back to the personal workspace.

## Expected Behavior

1. Conversations for repositories that belong to claimed organizations should be created in the organization's workspace
2. When provider resolution or org resolution fails, the system should log a warning and fall back to using the personal workspace
3. The error message "Failed to resolve org" should be logged when org resolution encounters an exception

## Relevant Import Paths

The solution requires imports from these modules (exact paths must be used):
- `from integrations.resolver_org_router import resolve_org_for_repo`
- `from storage.saas_conversation_store import SaasConversationStore`
- `from openhands.integrations.provider import ProviderHandler`
- `from uuid import uuid4`
- `from openhands.utils.conversation_summary import get_default_conversation_title`
- `from openhands.server.services.conversation_service import start_conversation`

## Testing

The repository includes tests that validate this behavior:
- `enterprise/tests/unit/integrations/linear/test_linear_view.py` - Unit tests for the modified method
- `enterprise/tests/unit/test_linear_view.py` - Tests for org routing logic

Run enterprise tests with: `cd enterprise && PYTHONPATH=".:$PYTHONPATH" poetry run pytest tests/unit/integrations/linear/`