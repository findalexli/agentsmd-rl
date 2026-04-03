#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'pub fn compress_into_buffer(block: &\[u8\], buffer: &mut Vec<u8>)' turbopack/crates/turbo-persistence/src/compression.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the PR diff from GitHub and apply it
curl -sL "https://github.com/vercel/next.js/pull/90608.diff" | git apply --whitespace=fix -

echo "Patch applied successfully."
