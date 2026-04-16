# Task: Route Jira Resolver Conversations to Claimed Organization Workspaces

## Problem

The Jira integration's `create_or_update_conversation` function in `enterprise/integrations/jira/jira_view.py` always creates conversations in the user's personal workspace. When a repository belongs to a Git organization that has been claimed by an organization (and the requesting user is a member), the conversation should be routed to that organization's workspace instead.

## Requirements for jira_view.py

The file `enterprise/integrations/jira/jira_view.py` must contain the following imports and logic in its `create_or_update_conversation` function:

### Required Imports

The file must include these imports:
- `resolve_org_for_repo` from `integrations.resolver_org_router`
- `SaasConversationStore` from `storage.saas_conversation_store`
- `ConversationMetadata` from the `conversation_metadata` module
- `start_conversation` from the `conversation_service` module
- `uuid4` from the `uuid` module

The file must **not** import `create_new_conversation`.

### Routing Logic

The `create_or_update_conversation` function must:
- Call `resolve_org_for_repo` to determine the target organization for a given repository
- Generate the conversation ID using `uuid4().hex`
- Create a `ConversationMetadata` instance that includes a `git_provider` keyword argument
- Obtain a conversation store via `SaasConversationStore.get_resolver_instance`
- Call `start_conversation` to create the conversation

The file must **not** call `create_new_conversation` anywhere.

### Routing Behavior

- When the repository belongs to a Git organization that has been claimed by an organization, and the requesting user is a member of that organization, the conversation should be routed to the claimed organization's workspace
- Otherwise, the conversation should be created in the user's personal workspace

## Test Requirements

Add routing tests to `enterprise/tests/unit/integrations/jira/test_jira_view.py` with:
- A test class named `TestJiraV0ConversationRouting`
- A test method named `test_routes_to_claimed_org_when_user_is_member` — verifies that when a repo belongs to a claimed org and the user is a member, the conversation is routed to that org's workspace
- A test method named `test_falls_back_to_personal_workspace_when_no_claim` — verifies that when no org has claimed the git org, the conversation goes to the personal workspace
- Import `ProviderType` from a module whose name contains `service_types`
- Use `unittest.mock.patch` to mock the new dependencies, with patch targets pointing to the Jira view module under test
- Use `AsyncMock` for async function mocks
- The test file must reference `resolve_org_for_repo`, `SaasConversationStore.get_resolver_instance`, and include the patch decorator `@patch('integrations.jira.jira_view.start_conversation')`

Do NOT modify any other files.
