#!/usr/bin/env bash
# Runtime environment setup - runs when container starts
set -e

echo "Setting up runtime environment..."

# Ensure we're in the sui repo directory
cd /workspace/sui

# Verify the repo is at the correct commit
CURRENT_COMMIT=$(git rev-parse HEAD)
EXPECTED_COMMIT="383a983d2b14715a4299227920188aa62089a723"

if [ "$CURRENT_COMMIT" != "$EXPECTED_COMMIT" ]; then
    echo "Warning: Current commit ($CURRENT_COMMIT) doesn't match expected ($EXPECTED_COMMIT)"
    echo "Checking out expected commit..."
    git checkout "$EXPECTED_COMMIT"
fi

echo "Repository is at commit: $(git rev-parse --short HEAD)"
echo "Runtime environment setup complete"
