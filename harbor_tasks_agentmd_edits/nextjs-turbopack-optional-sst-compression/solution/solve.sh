#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nextjs

# Idempotent: skip if ArcBytes already exists
if [ -f "turbopack/crates/turbo-persistence/src/arc_bytes.rs" ]; then
    echo "Patch already applied."
    exit 0
fi

# Fetch and apply the actual PR patch
curl -sL "https://github.com/vercel/next.js/pull/89309.diff" | git apply -

echo "Patch applied successfully."
