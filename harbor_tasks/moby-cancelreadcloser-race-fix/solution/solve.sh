#!/bin/bash
set -e

cd /workspace/moby

# Apply the gold fix for race condition in cancelReadCloser
# Change crc.Close() to crc.close() in the AfterFunc callback
sed -i 's/crc.stop = context.AfterFunc(ctx, func() { _ = crc.Close() })/crc.stop = context.AfterFunc(ctx, func() { _ = crc.close() })/' client/utils.go

# Verify the fix was applied
if ! grep -q "_ = crc.close()" client/utils.go; then
    echo "ERROR: Fix was not applied successfully"
    exit 1
fi

# Verify we didn't accidentally break anything
if grep -q "_ = crc.Close()" client/utils.go; then
    echo "ERROR: Old code still present"
    exit 1
fi

echo "Fix applied successfully"
