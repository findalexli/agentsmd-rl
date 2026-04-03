#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'checksum_block' turbopack/crates/turbo-persistence/src/compression.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit and apply the diff against base
git fetch --depth=1 origin ea56922a398e4dc682c0a3aeddaeefa42c747f12
git diff HEAD ea56922a398e4dc682c0a3aeddaeefa42c747f12 -- \
    Cargo.lock Cargo.toml \
    turbopack/crates/turbo-persistence/ | git apply

echo "Patch applied successfully."
