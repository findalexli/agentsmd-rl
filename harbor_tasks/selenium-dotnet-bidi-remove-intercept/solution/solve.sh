#!/bin/bash
set -e

cd /workspace/selenium

# Check if already at the merge commit (idempotency check)
current_commit=$(git rev-parse HEAD)
if [ "$current_commit" = "4a4c5939467b98db4c16f40f6d3c26626964c91b" ]; then
    echo "Already at merge commit"
    exit 0
fi

# Check if the high-level methods are already removed
if [ ! -f "dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs" ]; then
    echo "Patch already applied (HighLevel file missing)"
    exit 0
fi

# Apply the fix by checking out the merge commit
git checkout 4a4c5939467b98db4c16f40f6d3c26626964c91b

echo "Patch applied successfully - now at merge commit"
