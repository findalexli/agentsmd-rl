#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied
if grep -q "BASE_ARROW_MIN_LENGTH = 10" packages/element/src/binding.ts 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Fetch and checkout the merge commit (which includes the fix)
git fetch --depth=1 origin 5852d0d41005e67ca00124079b9eee91e4ab716d
git checkout 5852d0d41005e67ca00124079b9eee91e4ab716d

echo "Fix applied - now at merge commit with the fix"
