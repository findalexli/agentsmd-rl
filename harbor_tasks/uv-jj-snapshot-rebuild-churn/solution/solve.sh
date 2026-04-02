#!/usr/bin/env bash
set -euo pipefail

cd /repo

FILE="crates/uv-cli/build.rs"

# Idempotency: check if the fix is already applied
if grep -q '\.jj' "$FILE"; then
    echo "Fix already applied."
    exit 0
fi

# Insert the .jj early-return guard after the .git early-return block.
# The anchor is the closing brace of: if !git_dir.exists() { return; }
# We insert the new block right after the blank line following that closing brace.
sed -i '/^    if !git_dir\.exists() {/{
N;N
s|}$|}\
\
    // If in a jj repository, do not attempt to retrieve commit information because they snapshot\
    // frequently and will cause unnecessary rebuilds.\
    let jj_dir = workspace_root.join(".jj");\
    if jj_dir.exists() {\
        return;\
    }|
}' "$FILE"

echo "Fix applied successfully."
