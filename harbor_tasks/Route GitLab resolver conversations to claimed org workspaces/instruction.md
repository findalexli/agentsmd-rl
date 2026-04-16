# GitLab Resolver Organization Routing

## Problem

The GitLab integration creates resolver conversations without routing them to the correct organization's workspace. When a GitLab webhook arrives, the system should determine which organization has claimed the GitLab repository, then route the conversation to that organization's workspace — falling back to the user's personal workspace when no claim exists. Currently, conversations are created without any organization context.

There is also a parameter naming mismatch in the GitHub integration's callback processor: the summary instruction flag is passed under a keyword argument name that the receiving callback does not recognize, so the flag is never received.

## Symptoms

### Missing Organization Resolution

The GitLab integration does not resolve which organization has claimed the repository before creating a conversation. The codebase provides `resolve_org_for_repo` in `integrations.resolver_org_router` for determining org ownership. It accepts keyword arguments:

- `provider`: the Git provider identifier — `'gitlab'` for GitLab
- `full_repo_name`: the full repository name
- `keycloak_user_id`: the user's Keycloak identifier

The resolved organization ID must be stored as an instance attribute so it is available in both the V0 and V1 conversation creation paths.

### Non-Organization-Aware Conversation Creation

The current conversation creation path is not organization-aware and cannot route conversations to the correct org's workspace. The codebase provides `SaasConversationStore` in `storage.saas_conversation_store` for org-scoped resolver conversation management. This mechanism must be used instead of the generic conversation initialization path, which lacks organization routing support.

A `ConversationMetadata` object should be constructed directly with:

- `trigger`: set to `ConversationTrigger.RESOLVER`
- `git_provider`: set to `ProviderType.GITLAB`
- `conversation_id`: a freshly generated UUID in hex format
- `user_id`: the user's Keycloak ID
- `selected_repository`: the full repo name
- `selected_branch`: the branch name
- `title`: obtained via `get_default_conversation_title` from `openhands.utils.conversation_summary`

The metadata should be persisted through the conversation store's save mechanism.

### V1 Path Missing Organization Context

The V1 conversation creation path constructs a `ResolverUserContext` without the resolved organization ID, so the V1 resolver also operates without organization context. The resolved organization ID must be passed to the `ResolverUserContext` constructor.

### GitHub Callback Parameter Mismatch

The GitHub integration's callback processor passes the summary instruction flag under a keyword argument name that doesn't match what the receiving callback expects. The argument names must be aligned so the flag is correctly propagated.
