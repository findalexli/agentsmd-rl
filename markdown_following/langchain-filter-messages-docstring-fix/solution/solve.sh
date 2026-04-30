#!/bin/bash
set -e

cd /workspace/langchain

# Apply the fix using sed
# Replace the incorrect parameter names in the docstring example
sed -i 's/incl_names=/include_names=/g' libs/core/langchain_core/messages/utils.py
sed -i 's/incl_types=/include_types=/g' libs/core/langchain_core/messages/utils.py
sed -i 's/excl_ids=/exclude_ids=/g' libs/core/langchain_core/messages/utils.py

# Configure git for the commit
git config user.email "test@example.com"
git config user.name "Test User"

# Stage and commit the changes
git add libs/core/langchain_core/messages/utils.py
git commit -m "fix(core): correct parameter names in filter_messages docstring example

Fixed incorrect parameter names in the docstring example:
- incl_names -> include_names
- incl_types -> include_types
- excl_ids -> exclude_ids"

# Verify the patch was applied
grep -q "include_names=" libs/core/langchain_core/messages/utils.py && echo "Patch applied successfully"
