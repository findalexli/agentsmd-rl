# Slack Resolver Org Routing

## Problem

When a Slack resolver request includes a selected repository, the system should check whether the repository's Git organization is claimed by an OpenHands organization and whether the requesting user is a member of that organization. If both conditions are met, the conversation should be created in that organization's workspace; otherwise it should fall back to the user's personal workspace.

Currently, the Slack view does not implement this org routing logic. The V0 and V1 conversation creation paths fail to:

1. Resolve the target organization based on the selected repository's Git organization
2. Route the conversation to the claiming org's workspace (if the user is a member)
3. Fall back to the user's personal workspace if no claim exists

## Required Behavior

The implementation must use the following components:

- Import `resolve_org_for_repo` from `integrations.resolver_org_router` - utility to resolve the target organization
- Import `SaasConversationStore` from `storage.saas_conversation_store` - conversation store for resolver instances
- Import `start_conversation` from `openhands.server.services.conversation_service` (replacing any usage of `create_new_conversation`)
- Import `ConversationMetadata` from `openhands.storage.data_models.conversation_metadata`

When a repository is selected:
1. The git provider must be resolved early in the flow and stored in an instance attribute named `_resolved_git_provider` (with underscore prefix) for use by both V0 and V1 paths
2. The target organization must be resolved using `resolve_org_for_repo()` and stored in an instance attribute named `resolved_org_id` (without underscore prefix)
3. The resolved org ID must be passed through to both V0 and V1 conversation creation paths

For the V0 conversation path:
- Must use `SaasConversationStore.get_resolver_instance(config, user_id, resolver_org_id)` passing the resolved org ID as the third argument
- Must create a `ConversationMetadata` object with appropriate trigger, title, user ID, repository, and git provider
- Must persist the metadata via `store.save_metadata()` before starting the conversation
- Must call `start_conversation()` (replacing any usage of `create_new_conversation`)
- Must reference `start_conversation` as an awaited call: `await start_conversation(`

For the V1 conversation path:
- Must use the pre-resolved git provider from the `_resolved_git_provider` attribute (accessed via `self._resolved_git_provider`)
- Must pass `resolver_org_id` parameter to the `ResolverUserContext` constructor

When no repository is selected, skip org resolution and pass `None` for `resolver_org_id`.

## Files to Modify

- `enterprise/integrations/slack/slack_view.py` - Main implementation

## Testing

The tests verify that:
- `resolve_org_for_repo` is imported from `integrations.resolver_org_router` and called
- `SaasConversationStore` is imported from `storage.saas_conversation_store` and used via `get_resolver_instance()`
- `start_conversation` is imported and used (replacing `create_new_conversation`)
- `self.resolved_org_id` is set as an instance attribute
- `ConversationMetadata` is imported, instantiated, and saved via `store.save_metadata()`
- Git provider is resolved early and stored in `self._resolved_git_provider`
- The V1 path uses `self._resolved_git_provider` and passes `resolver_org_id` to `ResolverUserContext`
