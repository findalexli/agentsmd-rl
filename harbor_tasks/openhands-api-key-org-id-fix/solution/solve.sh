#!/bin/bash
set -e

cd /workspace/openhands

FILE="enterprise/server/utils/saas_app_conversation_info_injector.py"

# Check if fix is already applied (idempotency)
if grep -q "hasattr(self.user_context, 'user_auth')" "$FILE"; then
    echo "Fix already applied"
    exit 0
fi

# Read the file content
CONTENT=$(cat "$FILE")

# Find the line with "user = result.scalar_one_or_none()" and "assert user"
# We need to insert the org_id logic after these lines

# Use Python to make the edit reliably
python3 << 'EOF'
import re

file_path = "enterprise/server/utils/saas_app_conversation_info_injector.py"

with open(file_path, 'r') as f:
    content = f.read()

# The fix: insert org_id logic after the user assertion
old_block = '''            user = result.scalar_one_or_none()
            assert user

            # Check if SAAS metadata already exists'''

new_block = '''            user = result.scalar_one_or_none()
            assert user

            # Determine org_id: prefer API key's org_id if authenticated via API key
            org_id = user.current_org_id  # Default fallback
            if hasattr(self.user_context, 'user_auth'):
                user_auth = self.user_context.user_auth
                if hasattr(user_auth, 'get_api_key_org_id'):
                    api_key_org_id = user_auth.get_api_key_org_id()
                    if api_key_org_id is not None:
                        org_id = api_key_org_id

            # Check if SAAS metadata already exists'''

content = content.replace(old_block, new_block)

# Replace user.current_org_id with org_id in the assertion
content = content.replace(
    'existing_saas_metadata.user_id == user_id_uuid\n                and existing_saas_metadata.org_id == user.current_org_id',
    'existing_saas_metadata.user_id == user_id_uuid\n                and existing_saas_metadata.org_id == org_id'
)

# Replace org_id in the SAAS metadata creation
content = content.replace(
    '''            if not existing_saas_metadata:
                # Create new SAAS metadata
                # Set org_id to user_id as specified in requirements
                saas_metadata = StoredConversationMetadataSaas(
                    conversation_id=str(info.id),
                    user_id=user_id_uuid,
                    org_id=user.current_org_id,
                )''',
    '''            if not existing_saas_metadata:
                # Create new SAAS metadata with the determined org_id
                saas_metadata = StoredConversationMetadataSaas(
                    conversation_id=str(info.id),
                    user_id=user_id_uuid,
                    org_id=org_id,
                )'''
)

with open(file_path, 'w') as f:
    f.write(content)

print("Fix applied successfully")
EOF

# Verify the fix was applied
if ! grep -q "hasattr(self.user_context, 'user_auth')" "$FILE"; then
    echo "ERROR: Fix was not applied correctly"
    exit 1
fi

echo "Fix verified"
