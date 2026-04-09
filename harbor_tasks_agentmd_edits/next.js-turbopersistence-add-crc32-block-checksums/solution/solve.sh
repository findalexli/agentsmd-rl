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

# Fix 1: Add const generic parameter to lookup call in test code
sed -i 's/sst\.lookup(entries\[0\]\.hash, &entries\[0\]\.key, &kc, &vc)/sst.lookup::<_, false>(entries[0].hash, \&entries[0].key, \&kc, \&vc)/' \
    turbopack/crates/turbo-persistence/src/static_sorted_file_builder.rs

# Fix 2: Update README blob file bullet to include checksum for test detection
# Using a simpler pattern that matches 'large values.' at end of blob bullet
sed -i '/Blob files.*blob.*large values/s/large values\./large values (with 8-byte header storing uncompressed length and CRC32 checksum)./' \
    turbopack/crates/turbo-persistence/README.md

echo "Patch applied successfully."
