#!/bin/bash
set -e

cd /workspace/router

# Apply the fix to ssr-client.ts
python3 << 'PYTHON_SCRIPT'
import re

ssr_client_path = "packages/router-core/src/ssr/ssr-client.ts"
with open(ssr_client_path, "r") as f:
    content = f.read()

# Find the non-SPA block and add the resolvedLocation fix before the early return
# The block is:
#   if (!hasSsrFalseMatches && !isSpaMode) {
#     matches.forEach((match) => {
#       // remove the dehydrated flag since we won't run router.load() which would remove it
#       match._nonReactive.dehydrated = undefined
#     })
#     return routeChunkPromise
#   }

old_block = """  if (!hasSsrFalseMatches && !isSpaMode) {
    matches.forEach((match) => {
      // remove the dehydrated flag since we won't run router.load() which would remove it
      match._nonReactive.dehydrated = undefined
    })
    return routeChunkPromise
  }"""

new_block = """  if (!hasSsrFalseMatches && !isSpaMode) {
    matches.forEach((match) => {
      // remove the dehydrated flag since we won't run router.load() which would remove it
      match._nonReactive.dehydrated = undefined
    })
    // Mark the current location as resolved so that later load cycles
    // (e.g. preloads, invalidations) don't mistakenly detect a href change
    // (resolvedLocation defaults to undefined and router.load() is skipped
    // in the normal SSR hydration path).
    router.stores.resolvedLocation.setState(() => router.stores.location.state)
    return routeChunkPromise
  }"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(ssr_client_path, "w") as f:
        f.write(content)
    print("Applied ssr-client.ts fix")
else:
    # The fix is already applied (base commit might have it already?)
    # Check if the resolvedLocation.setState is present
    if "router.stores.resolvedLocation.setState(() => router.stores.location.state)" in content:
        print("Fix already present in ssr-client.ts")
    else:
        print("ERROR: Could not find the expected block in ssr-client.ts")
        import sys
        sys.exit(1)
PYTHON_SCRIPT

cd /workspace/router/packages/router-core
pnpm --filter @tanstack/router-core run build 2>&1 | tail -5