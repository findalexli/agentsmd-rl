#!/usr/bin/env bash
set -euo pipefail
cd /workspace/opencode

# Apply the gold patch from PR #19304
git apply /solution/gold.patch
