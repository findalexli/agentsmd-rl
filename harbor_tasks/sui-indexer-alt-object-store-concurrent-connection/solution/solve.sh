#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied (idempotency check)
if grep -q "async fn get_watermark_for_read" crates/sui-indexer-alt-object-store/src/lib.rs; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Fetch the file from the merge commit
curl -s "https://raw.githubusercontent.com/MystenLabs/sui/92cdfc7fe041bf824567e76995a5d5ef973bc6d6/crates/sui-indexer-alt-object-store/src/lib.rs" \
    -o crates/sui-indexer-alt-object-store/src/lib.rs

# Verify the download was successful
if ! grep -q "async fn get_watermark_for_read" crates/sui-indexer-alt-object-store/src/lib.rs; then
    echo "ERROR: Failed to download the fixed file"
    exit 1
fi

echo "Patch applied successfully"
