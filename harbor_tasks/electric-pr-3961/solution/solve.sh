#!/bin/bash
set -e
cd /workspace/electric

git fetch --depth=2 origin 0031e81777c0a93ab90161be5e6d0e9c999e00d2
git checkout 0031e81777c0a93ab90161be5e6d0e9c999e00d2

# Verify the distinctive line exists (idempotency check)
grep -q "createCacheBuster" packages/typescript-client/src/client.ts