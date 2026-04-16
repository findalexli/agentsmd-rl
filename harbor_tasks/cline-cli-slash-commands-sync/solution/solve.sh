#!/bin/bash
set -e

cd /workspace/cline

# Fetch and apply the gold patch from GitHub PR #9747
curl -sL "https://github.com/cline/cline/pull/9747.patch" -o /tmp/pr.patch

# Apply the patch
git apply /tmp/pr.patch

# Verify patch was applied
echo "Patch applied successfully. Modified files:"
git diff --stat HEAD
