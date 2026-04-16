#!/bin/bash
set -e

cd /workspace/bun

# Check if patch was already applied
if grep -q "sccache configured for bun-build-sccache-store" cmake/tools/SetupSccache.cmake 2>/dev/null; then
  echo "Patch already applied, skipping..."
  exit 0
fi

# Apply the gold patch from the PR
cd /workspace/bun

# The patch has a/ and b/ prefixes, we need to strip one level
git apply --verbose /solution/gold.patch || {
  echo "Git apply failed, trying with 3-way merge..."
  git apply --3way /solution/gold.patch || {
    echo "Full patch failed, trying partial application..."

    # Delete SetupCcache.cmake manually (this file doesn't exist in base, so git apply might fail on it)
    rm -f cmake/tools/SetupCcache.cmake

    # Re-try the patch with exclude for the deleted file
    git apply --verbose /solution/gold.patch 2>/dev/null || true
  }
}

echo "Patch applied successfully!"
