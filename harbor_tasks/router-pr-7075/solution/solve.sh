#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if already applied
if grep -q "inner.serialError || inner.firstBadMatchIndex != null" packages/router-core/src/load-matches.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Fix 1: Change the break condition to also check firstBadMatchIndex
# Original: if (inner.serialError) {
# Fixed:    if (inner.serialError || inner.firstBadMatchIndex != null) {
sed -i 's/if (inner\.serialError) {$/if (inner.serialError || inner.firstBadMatchIndex != null) {/' packages/router-core/src/load-matches.ts

# Fix 2: Change headMaxIndex to use firstBadMatchIndex directly instead of serialError
# Original (multi-line):
#   let headMaxIndex = inner.serialError
#     ? (inner.firstBadMatchIndex ?? 0)
#     : inner.matches.length - 1
# Fixed (multi-line):
#   let headMaxIndex =
#     inner.firstBadMatchIndex !== undefined
#       ? inner.firstBadMatchIndex
#       : inner.matches.length - 1

# Use perl for multi-line replacement
perl -i -0pe 's/let headMaxIndex = inner\.serialError\s*\n\s*\? \(inner\.firstBadMatchIndex \?\? 0\)\s*\n\s*: inner\.matches\.length - 1/let headMaxIndex =\n        inner.firstBadMatchIndex !== undefined\n          ? inner.firstBadMatchIndex\n          : inner.matches.length - 1/g' packages/router-core/src/load-matches.ts

echo "Patch applied successfully"

# Rebuild the affected package
pnpm nx run @tanstack/router-core:build
