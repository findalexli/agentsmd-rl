# GitLab Resolver Organization Routing

## Problem

The GitLab integration creates resolver conversations without routing them to the correct organization's workspace. When a GitLab webhook arrives, the system should determine which organization has claimed the GitLab repository, then route the conversation to that organization's workspace — falling back to the user's personal workspace when no claim exists. Currently, conversations are created without any organization context.

The root cause is that the GitLab view (`enterprise/integrations/gitlab/gitlab_view.py`) uses `initialize_conversation` from `openhands.server.services.conversation_service` to create conversations. This function is not organization-aware and cannot support the resolver workflow's org-routing requirements. The codebase provides `SaasConversationStore` (in `storage.saas_conversation_store`) specifically for organization-scoped resolver conversations — this must be used instead.

There is also a parameter naming inconsistency in the GitHub integration at `enterprise/integrations/github/github_view.py`: the callback processor passes the summary instruction flag as `send_summary_instruction=...`, but the receiving callback expects the keyword argument to be named `should_request_summary`.

## Requirements

### Organization Resolution

The system must resolve which organization owns the GitLab repository before creating a conversation. The function `resolve_org_for_repo` from `integrations.resolver_org_router` provides this capability. Its API contract expects keyword arguments:

- `provider`: the Git provider identifier — must be `'gitlab'`
- `full_repo_name`: the full repository name, available as `self.full_repo_name`
- `keycloak_user_id`: the user's Keycloak identifier, available as `self.user_info.keycloak_user_id`

The result — the resolved organization ID — must be stored as `self.resolved_org_id` so it is accessible throughout the conversation lifecycle (both V0 and V1 paths).

### Organization-Aware Conversation Creation

The GitLab view must not import or use `initialize_conversation` from `openhands.server.services.conversation_service`. Only `start_conversation` from that module is still needed.

Instead, conversations must be created through `SaasConversationStore.get_resolver_instance`, which accepts the resolved org ID and returns an org-scoped conversation store. The conversation ID must be generated as a hex string via `uuid4().hex`.

A `ConversationMetadata` object must be constructed directly (not via `initialize_conversation`) with these fields:

- `trigger`: `ConversationTrigger.RESOLVER`
- `git_provider`: `ProviderType.GITLAB`
- `conversation_id`: the generated hex UUID
- `user_id`: the user's Keycloak ID
- `selected_repository`: the full repo name
- `selected_branch`: the branch name
- `title`: obtained via `get_default_conversation_title` (from `openhands.utils.conversation_summary`)

The metadata must be persisted by calling `store.save_metadata(conversation_metadata)`.

### V1 Path Organization Context

When creating a V1 conversation, the `ResolverUserContext` constructor must receive the resolved organization ID via its `resolver_org_id` keyword argument, using the value stored as `self.resolved_org_id` during initialization.

### GitHub Callback Parameter Naming

The GitHub callback processor must use `should_request_summary` (not `send_summary_instruction`) as the keyword argument name when passing the summary instruction flag. The value should remain `self.send_summary_instruction`.
