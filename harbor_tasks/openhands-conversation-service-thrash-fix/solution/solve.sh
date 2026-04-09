#!/bin/bash
set -e

cd /workspace/openhands

# Check if patch already applied (idempotency check)
if grep -q "app_conversation_info_service_dependency = depends_app_conversation_info_service()" openhands/server/routes/conversation.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch using Python for reliability
python3 <<'PYTHON'
import re

file_path = "openhands/server/routes/conversation.py"
with open(file_path, 'r') as f:
    content = f.read()

# 1. Replace imports
old_imports = '''from openhands.app_server.app_conversation.app_conversation_service import (
    AppConversationService,
)
from openhands.app_server.config import depends_app_conversation_service'''

new_imports = '''from openhands.app_server.app_conversation.app_conversation_info_service import (
    AppConversationInfoService,
)
from openhands.app_server.app_conversation.app_conversation_models import (
    AppConversationInfo,
)
from openhands.app_server.config import depends_app_conversation_info_service'''

content = content.replace(old_imports, new_imports)

# 2. Replace dependency
content = content.replace(
    'app_conversation_service_dependency = depends_app_conversation_service()',
    'app_conversation_info_service_dependency = depends_app_conversation_info_service()'
)

# 3. Replace _is_v1_conversation and _get_v1_conversation_config with _get_v1_conversation_info
old_helpers = '''async def _is_v1_conversation(
    conversation_id: str, app_conversation_service: AppConversationService
) -> bool:
    """Check if the given conversation_id corresponds to a V1 conversation.

    Args:
        conversation_id: The conversation ID to check
        app_conversation_service: Service to query V1 conversations

    Returns:
        True if this is a V1 conversation, False otherwise
    """
    try:
        conversation_uuid = uuid.UUID(conversation_id)
        app_conversation = await app_conversation_service.get_app_conversation(
            conversation_uuid
        )
        return app_conversation is not None
    except (ValueError, TypeError):
        # Not a valid UUID, so it's not a V1 conversation
        return False
    except Exception:
        # Service error, assume it's not a V1 conversation
        return False


async def _get_v1_conversation_config(
    conversation_id: str, app_conversation_service: AppConversationService
) -> dict[str, str | None]:
    """Get configuration for a V1 conversation.

    Args:
        conversation_id: The conversation ID
        app_conversation_service: Service to query V1 conversations

    Returns:
        Dictionary with runtime_id (sandbox_id) and session_id (conversation_id)
    """
    conversation_uuid = uuid.UUID(conversation_id)
    app_conversation = await app_conversation_service.get_app_conversation(
        conversation_uuid
    )

    if app_conversation is None:
        raise ValueError(f'V1 conversation {conversation_id} not found')

    return {
        'runtime_id': app_conversation.sandbox_id,
        'session_id': conversation_id,
    }'''

new_helper = '''async def _get_v1_conversation_info(
    conversation_id: str, app_conversation_info_service: AppConversationInfoService
) -> AppConversationInfo | None:
    try:
        conversation_uuid = uuid.UUID(conversation_id)
        app_conversation_info = (
            await app_conversation_info_service.get_app_conversation_info(
                conversation_uuid
            )
        )
        return app_conversation_info
    except (ValueError, TypeError):
        # Not a valid UUID, so it's not a V1 conversation
        return None
    except Exception as e:
        # Service error, assume it's not a V1 conversation
        logger.debug(f'Failed to fetch V1 conversation {conversation_id}: {e}')
        return None'''

content = content.replace(old_helpers, new_helper)

# 4. Update get_remote_runtime_config signature
content = content.replace(
    'app_conversation_service: AppConversationService = app_conversation_service_dependency,',
    'app_conversation_info_service: AppConversationInfoService = app_conversation_info_service_dependency,'
)

# 5. Update the endpoint body
old_body = '''    # Check if this is a V1 conversation first
    if await _is_v1_conversation(conversation_id, app_conversation_service):
        # This is a V1 conversation
        config = await _get_v1_conversation_config(
            conversation_id, app_conversation_service
        )
    else:'''

new_body = '''    # Check if this is a V1 conversation first
    v1_conversation_info = await _get_v1_conversation_info(
        conversation_id, app_conversation_info_service
    )
    if v1_conversation_info:
        # This is a V1 conversation
        return JSONResponse(
            content={
                'runtime_id': v1_conversation_info.sandbox_id,
                'session_id': conversation_id,
            },
            status_code=200,
        )
    else:'''

content = content.replace(old_body, new_body)

with open(file_path, 'w') as f:
    f.write(content)

print("Patch applied successfully")
PYTHON
