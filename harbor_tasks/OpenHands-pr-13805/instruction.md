# Task: Route Jira Resolver Conversations to Claimed Organization Workspaces

## Problem

The Jira integration creates conversations for issues, but currently all conversations are created in the user's personal workspace regardless of repository ownership. This causes problems when a repository belongs to a Git organization that has been claimed by an organization in the system - the conversation should be created in that organization's workspace instead.

When a repository belongs to a Git organization that has been claimed by an organization, and the requesting user is a member of that organization, the Jira resolver should route the conversation to that organization's workspace. If no organization has claimed the git organization, the conversation should fall back to the user's personal workspace.

## Requirements

### Functional Requirements

1. **Organization Resolution**: The system must determine if a repository belongs to a Git organization that has been claimed by an organization in the system. This requires calling the organization resolution function with the git provider, repository name, and user ID.

2. **Membership Check**: The requesting user must be a member of the claimed organization for the routing to occur.

3. **Routing Behavior**:
   - When repository belongs to a claimed Git organization AND user is a member → route to organization's workspace
   - When no organization has claimed the Git organization → fall back to personal workspace
   - When user is not a member of claimed organization → fall back to personal workspace

4. **Conversation Metadata**: The conversation metadata must include the git provider information (e.g., 'github', 'gitlab') so the system knows which provider was used to resolve the repository. The metadata must include a `git_provider` field.

5. **Conversation ID Generation**: Conversation IDs must be generated as UUID4 hex strings (32-character hexadecimal format), using `uuid4().hex`.

6. **API Transition**: The implementation must use the `start_conversation` function from the conversation service API (not `create_new_conversation`).

### Implementation Details

The following imports and function calls are required in `jira_view.py`:

- Import `resolve_org_for_repo` from `integrations.resolver_org_router`
- Import `SaasConversationStore` from `storage.saas_conversation_store`
- Import `ConversationMetadata` from `openhands.storage.data_models.conversation_metadata`
- Import `uuid4` from `uuid` module
- Import `start_conversation` from `openhands.server.services.conversation_service` (replacing any `create_new_conversation` import)
- Call `resolve_org_for_repo` with `provider`, `full_repo_name`, and `keycloak_user_id` parameters
- Call `SaasConversationStore.get_resolver_instance()` with configuration, user ID, and resolved org ID
- Create a `ConversationMetadata` instance with a `git_provider` field
- Use `uuid4().hex` to generate the conversation ID

### Test Requirements

Add routing tests to `enterprise/tests/unit/integrations/jira/test_jira_view.py` with:
- A test class named `TestJiraV0ConversationRouting`
- A test method named `test_routes_to_claimed_org_when_user_is_member` — verifies routing to claimed org workspace when user is member
- A test method named `test_falls_back_to_personal_workspace_when_no_claim` — verifies fallback to personal workspace when no claim exists
- Import `ProviderType` from `openhands.integrations.service_types`
- Import `UserAuth` from `openhands.server.user_auth.user_auth`
- Use `unittest.mock.patch` to mock dependencies, with patch targets pointing to `integrations.jira.jira_view` module under test
- Use `AsyncMock` for async function mocks
- Patch targets must include:
  - `integrations.jira.jira_view.resolve_org_for_repo`
  - `integrations.jira.jira_view.SaasConversationStore.get_resolver_instance`
  - `integrations.jira.jira_view.start_conversation`
  - `integrations.jira.jira_view.ProviderHandler`
  - `integrations.jira.jira_view.integration_store`

The routing tests should verify that when `resolve_org_for_repo` returns an organization ID, the `SaasConversationStore.get_resolver_instance` is called with that org ID, and when `resolve_org_for_repo` returns `None`, the store is called with `None` for the org ID.

Do NOT modify any other files.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
