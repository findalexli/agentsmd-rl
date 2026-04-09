# Slack Resolver Org Routing

## Problem

When a Slack resolver request includes a selected repository, the system needs to check whether the repository's Git organization is claimed by an OpenHands organization and whether the requesting user is a member of that organization. If both conditions are met, the conversation should be created in that organization's workspace; otherwise it should fall back to the user's personal workspace.

Currently, the Slack view (`enterprise/integrations/slack/slack_view.py`) does not implement this org routing logic. The V0 and V1 conversation creation paths need to:

1. Resolve the target organization based on the selected repository's Git organization
2. Route the conversation to the claiming org's workspace (if the user is a member)
3. Fall back to the user's personal workspace if no claim exists

## Your Task

Modify `enterprise/integrations/slack/slack_view.py` to implement org routing for Slack resolver conversations:

1. **Early git provider resolution**: Determine the git provider from the selected repository early in the flow (in `create_or_update_conversation`) and store it for use by both V0 and V1 paths

2. **Org resolution**: Use the `resolve_org_for_repo` utility to determine the target org based on the repo's Git organization and the user's membership

3. **V0 path changes**: 
   - Replace the call to `create_new_conversation` with manual conversation creation using `SaasConversationStore.get_resolver_instance()` and `start_conversation()`
   - Pass `resolver_org_id` to `get_resolver_instance()`
   - Create and save `ConversationMetadata` before starting the conversation

4. **V1 path changes**:
   - Use the pre-resolved git provider instead of computing it locally
   - Pass `resolver_org_id` to `ResolverUserContext`

5. **Handle no-repo case**: When no repository is selected, skip org resolution and pass `None` for `resolver_org_id`

## Files to Modify

- `enterprise/integrations/slack/slack_view.py` - Main implementation

## Testing

The tests verify that:
- `resolve_org_for_repo` is imported and called
- `SaasConversationStore` is imported and used
- `start_conversation` replaces `create_new_conversation`
- `resolver_org_id` is passed through both V0 and V1 paths
- `ConversationMetadata` is created and saved
- Git provider is resolved early and reused

## Hints

- Look at the imports section - you'll need to add several new imports
- The `create_or_update_conversation` method should resolve the org and store it in an instance variable
- The `_create_v0_conversation` method needs significant refactoring to use the new conversation creation pattern
- The `_create_v1_conversation` method should reuse the pre-resolved git provider
- Check for the `ResolverUserContext` constructor signature to see what parameters it accepts
