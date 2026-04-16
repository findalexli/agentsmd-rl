#!/bin/bash
set -euo pipefail

cd /workspace/openai-agents-js

# Fetch the merge commit and checkout to it
git fetch --filter=blob:none origin 4e00b3ca2a54dd7842924d61d15f3898abf46d2f
git checkout 4e00b3ca2a54dd7842924d61d15f3898abf46d2f

# Re-install and rebuild with the fix
pnpm install --frozen-lockfile
pnpm build
