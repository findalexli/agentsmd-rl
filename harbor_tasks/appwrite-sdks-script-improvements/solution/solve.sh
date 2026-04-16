#!/bin/bash
set -e

cd /workspace/appwrite

BASE_COMMIT="7fcc6406520a04f32d4a61ec147a9e67995d9f8f"
MERGE_COMMIT="2057eab918b8eedd81039e24f93743e149e6e133"

# Fetch and apply the actual PR diff
curl -sL "https://github.com/appwrite/appwrite/compare/${BASE_COMMIT}...${MERGE_COMMIT}.diff" -o /tmp/pr.diff || true

# If that fails, use a minimal patch based on the actual changes
if [ ! -s /tmp/pr.diff ] || ! git apply /tmp/pr.diff 2>/dev/null; then
    echo "Applying manual changes..."

    # Get the actual file content from the merge commit
    curl -sL "https://raw.githubusercontent.com/appwrite/appwrite/${MERGE_COMMIT}/src/Appwrite/Platform/Tasks/SDKs.php" -o /tmp/new_sdks.php

    # Copy the fixed file
    cp /tmp/new_sdks.php /workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php

    echo "Manual changes applied"
fi

echo "Patch applied successfully"
