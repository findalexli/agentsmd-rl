#!/bin/bash
set -e

cd /workspace/continue/extensions/cli

# Copy the updated resolveReviews.ts
cp /solution/resolveReviews.ts src/commands/review/resolveReviews.ts

# Copy the test file
cp /solution/resolveReviews.test.ts src/commands/review/resolveReviews.test.ts

# Verify the files were created correctly
grep -qF ".continue/checks/*.md" src/commands/review/resolveReviews.ts || grep -q ".continue/checks/" src/commands/review/resolveReviews.ts
grep -q "discovers files from .continue/checks/" src/commands/review/resolveReviews.test.ts
echo "Patch applied successfully"
