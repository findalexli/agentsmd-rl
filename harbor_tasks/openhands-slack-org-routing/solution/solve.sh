#!/bin/bash
set -e

cd /workspace/openhands

python3 << 'PYEOF'
import re

# Read the original file
with open('/workspace/openhands/enterprise/integrations/slack/slack_view.py', 'r') as f:
    lines = f.readlines()

content = ''.join(lines)

# 1. Add new imports - carefully match exact patterns
# Add resolve_org_for_repo import
content = content.replace(
    'from integrations.resolver_context import ResolverUserContext',
    'from integrations.resolver_context import ResolverUserContext\nfrom integrations.resolver_org_router import resolve_org_for_repo'
)

# Add server.config import
content = content.replace(
    'from jinja2 import Environment',
    'from jinja2 import Environment\nfrom server.config import get_config'
)

# Add SaasConversationStore import
content = content.replace(
    'from slack_sdk import WebClient',
    'from slack_sdk import WebClient\nfrom storage.saas_conversation_store import SaasConversationStore'
)

# Change ProviderHandler import (remove ProviderType)
content = content.replace(
    'from openhands.integrations.provider import ProviderHandler, ProviderType',
    'from openhands.integrations.provider import ProviderHandler'
)

# Update conversation_service imports - need to match multi-line pattern
content = content.replace(
    '''from openhands.server.services.conversation_service import (
    create_new_conversation,
    setup_init_conversation_settings,
)''',
    '''from openhands.server.services.conversation_service import (
    setup_init_conversation_settings,
    start_conversation,
)'''
)

# Add ConversationMetadata import
content = content.replace(
    '''from openhands.storage.data_models.conversation_metadata import (
    ConversationTrigger,
)''',
    '''from openhands.storage.data_models.conversation_metadata import (
    ConversationMetadata,
    ConversationTrigger,
)'''
)

# Add get_default_conversation_title import
content = content.replace(
    'from openhands.utils.async_utils import GENERAL_TIMEOUT',
    'from openhands.utils.async_utils import GENERAL_TIMEOUT\nfrom openhands.utils.conversation_summary import get_default_conversation_title'
)

# 2. Add the git provider and org resolution section after "user_secrets = await self.saas_user_auth.get_secrets()"
old_check = '''        user_secrets = await self.saas_user_auth.get_secrets()

        # Check if V1 conversations are enabled for this user'''

new_check = '''        user_secrets = await self.saas_user_auth.get_secrets()

        # Determine git provider from repository (needed for both org routing and conversation creation)
        self._resolved_git_provider = None
        if self.selected_repo and provider_tokens:
            provider_handler = ProviderHandler(provider_tokens)
            repository = await provider_handler.verify_repo_provider(self.selected_repo)
            self._resolved_git_provider = repository.git_provider

        # Resolve target org based on claimed git organizations
        self.resolved_org_id = None
        if self._resolved_git_provider and self.selected_repo:
            self.resolved_org_id = await resolve_org_for_repo(
                provider=self._resolved_git_provider.value,
                full_repo_name=self.selected_repo,
                keycloak_user_id=self.slack_to_openhands_user.keycloak_user_id,
            )

        # Check if V1 conversations are enabled for this user'''

content = content.replace(old_check, new_check)

# 3. Replace the V0 conversation creation - use a more flexible pattern
# The key markers are: "# Determine git provider from repository" block and "agent_loop_info = await create_new_conversation"
old_v0 = '''        # Determine git provider from repository
        git_provider = None
        if self.selected_repo and provider_tokens:
            provider_handler = ProviderHandler(provider_tokens)
            repository = await provider_handler.verify_repo_provider(self.selected_repo)
            git_provider = repository.git_provider

        agent_loop_info = await create_new_conversation(
            user_id=self.slack_to_openhands_user.keycloak_user_id,
            git_provider_tokens=provider_tokens,
            selected_repository=self.selected_repo,
            selected_branch=None,
            initial_user_msg=user_instructions,
            conversation_instructions=(
                conversation_instructions if conversation_instructions else None
            ),
            image_urls=None,
            replay_json=None,
            conversation_trigger=ConversationTrigger.SLACK,
            custom_secrets=user_secrets.custom_secrets if user_secrets else None,
            git_provider=git_provider,
        )

        self.conversation_id = agent_loop_info.conversation_id'''

new_v0 = '''        user_id = self.slack_to_openhands_user.keycloak_user_id

        # Create the conversation store with resolver org routing
        # (bypasses initialize_conversation to avoid threading enterprise-only
        # resolver_org_id through the generic OSS interface)
        store = await SaasConversationStore.get_resolver_instance(
            get_config(),
            user_id,
            self.resolved_org_id,
        )

        conversation_id = uuid4().hex
        conversation_metadata = ConversationMetadata(
            trigger=ConversationTrigger.SLACK,
            conversation_id=conversation_id,
            title=get_default_conversation_title(conversation_id),
            user_id=user_id,
            selected_repository=self.selected_repo,
            selected_branch=None,
            git_provider=self._resolved_git_provider,
        )
        await store.save_metadata(conversation_metadata)

        await start_conversation(
            user_id=user_id,
            git_provider_tokens=provider_tokens,
            custom_secrets=user_secrets.custom_secrets if user_secrets else None,
            initial_user_msg=user_instructions,
            image_urls=None,
            replay_json=None,
            conversation_id=conversation_id,
            conversation_metadata=conversation_metadata,
            conversation_instructions=(
                conversation_instructions if conversation_instructions else None
            ),
        )

        self.conversation_id = conversation_id'''

content = content.replace(old_v0, new_v0)

# 4. Replace the V1 git provider code
old_v1_git = '''        # Determine git provider from repository
        git_provider = None
        provider_tokens = await self.saas_user_auth.get_provider_tokens()
        if self.selected_repo and provider_tokens:
            provider_handler = ProviderHandler(provider_tokens)
            repository = await provider_handler.verify_repo_provider(self.selected_repo)
            git_provider = ProviderType(repository.git_provider.value)'''

new_v1_git = '''        # Use git provider resolved in create_or_update_conversation
        git_provider = self._resolved_git_provider'''

content = content.replace(old_v1_git, new_v1_git)

# 5. Update ResolverUserContext creation in V1
old_v1_context = 'slack_user_context = ResolverUserContext(saas_user_auth=self.saas_user_auth)'
new_v1_context = '''slack_user_context = ResolverUserContext(
            saas_user_auth=self.saas_user_auth,
            resolver_org_id=self.resolved_org_id,
        )'''

content = content.replace(old_v1_context, new_v1_context)

# Write the modified content back
with open('/workspace/openhands/enterprise/integrations/slack/slack_view.py', 'w') as f:
    f.write(content)

print("Gold patch applied successfully via Python")
PYEOF

echo "Gold fix applied successfully"
