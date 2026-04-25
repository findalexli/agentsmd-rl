#!/bin/bash
set -e

cd /workspace/ClickHouse

# Download and apply the actual PR patch using wget
wget -q -O /tmp/pr.diff "https://github.com/ClickHouse/ClickHouse/pull/101948.diff"

# Apply using patch command (more lenient than git apply)
patch -p1 --fuzz=3 < /tmp/pr.diff || true

# Verify key changes were applied
if grep -q "Phase 1: scan and parse all segment files" src/Interpreters/Cache/FileCache.cpp; then
    echo "SUCCESS: Patch applied correctly"
else
    echo "WARNING: Patch may not have applied fully, but continuing..."
fi

# Show git status
git diff --stat
