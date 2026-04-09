# GitLab Resolver Organization Routing

The GitLab resolver needs to route conversations to the correct organization workspace when processing webhook events. Currently, it uses a generic `initialize_conversation` function that doesn't support organization-level routing.

## Problem

When a GitLab webhook arrives, the system needs to:
1. Extract the organization from the repository path (e.g., "OrgName/repo")
2. Check if an OpenHands organization has claimed that GitLab organization
3. Verify the requesting user is a member of the claiming org
4. Route the conversation to that organization's workspace if valid

If the user is not a member of the claiming org (or no claim exists), the conversation should fall back to the user's personal workspace.

## Files to Modify

### Primary: `enterprise/integrations/gitlab/gitlab_view.py`

The `GitlabIssue` class's `initialize_new_conversation` method needs to be updated:

1. **Add imports** at the top of the file:
   - `resolve_org_for_repo` from `integrations.resolver_org_router`
   - `SaasConversationStore` from `storage.saas_conversation_store`
   - `get_default_conversation_title` from `openhands.utils.conversation_summary`
   - Remove `initialize_conversation` from the `openhands.server.services.conversation_service` import (keep `start_conversation`)

2. **In `initialize_new_conversation` method**:
   - Call `resolve_org_for_repo(provider='gitlab', ...)` to determine the target organization
   - Store the result in `self.resolved_org_id`
   - Instead of calling `initialize_conversation()`, create the conversation store directly using `SaasConversationStore.get_resolver_instance(config, user_id, resolver_org_id)`
   - Generate a `conversation_id` using `uuid4().hex`
   - Create `ConversationMetadata` manually with all required fields (including `trigger=ConversationTrigger.RESOLVER`, `git_provider=ProviderType.GITLAB`)
   - Save the metadata via `store.save_metadata()`
   - Store `conversation_id` in `self.conversation_id`

3. **In `_create_v1_conversation` method**:
   - Pass `resolver_org_id=self.resolved_org_id` to the `ResolverUserContext` constructor

4. **In `_create_gitlab_v1_callback_processor` method**:
   - Rename parameter `send_summary_instruction` to `should_request_summary` (to match the expected interface)

### Secondary: `enterprise/integrations/github/github_view.py`

For consistency across providers, update the GitHub callback processor methods:
- In both `_create_github_v1_callback_processor` instances, rename `send_summary_instruction=` to `should_request_summary=`

## Expected Behavior

After the fix:
- V0 path (non-v1): `initialize_new_conversation` resolves the org, creates a store with that org context, and saves metadata there
- V1 path: `resolved_org_id` is available on the instance and passed to `ResolverUserContext`
- The same routing logic works for both GitLab issues and merge requests

## Testing Reference

The PR includes tests in `enterprise/tests/unit/test_gitlab_view.py` that verify:
1. V0 path passes `resolver_org_id` to `get_resolver_instance`
2. V1 path passes `resolver_org_id` to `ResolverUserContext`
3. When no claim exists, `resolver_org_id` is `None` (fallback to personal workspace)
