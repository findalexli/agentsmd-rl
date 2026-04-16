#!/bin/bash
set -e

# Apply the fix for openrouter SDK API changes
cd /workspace/langchain/libs/partners/openrouter

# Check if already applied (idempotency)
if grep -q "components.ChatUserMessage" langchain_openrouter/chat_models.py 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Apply the patch using sed to update the role_to_model mapping
sed -i 's/components\.UserMessage/components.ChatUserMessage/g' langchain_openrouter/chat_models.py
sed -i 's/components\.SystemMessage/components.ChatSystemMessage/g' langchain_openrouter/chat_models.py
sed -i 's/components\.AssistantMessage/components.ChatAssistantMessage/g' langchain_openrouter/chat_models.py
sed -i 's/components\.ToolResponseMessage/components.ChatToolMessage/g' langchain_openrouter/chat_models.py
sed -i 's/components\.DeveloperMessage/components.ChatDeveloperMessage/g' langchain_openrouter/chat_models.py

# Also update the test file
sed -i 's/components\.UserMessage/components.ChatUserMessage/g' tests/unit_tests/test_chat_models.py
sed -i 's/components\.SystemMessage/components.ChatSystemMessage/g' tests/unit_tests/test_chat_models.py
sed -i 's/components\.AssistantMessage/components.ChatAssistantMessage/g' tests/unit_tests/test_chat_models.py
sed -i 's/components\.ToolResponseMessage/components.ChatToolMessage/g' tests/unit_tests/test_chat_models.py
sed -i 's/components\.DeveloperMessage/components.ChatDeveloperMessage/g' tests/unit_tests/test_chat_models.py

# Update dependency version in pyproject.toml to require the new SDK version
sed -i 's/openrouter>=0.7.11/openrouter>=0.8.0/g' pyproject.toml

echo "Fix applied successfully"
