#!/bin/bash
# Fix script for ruff repository - removes intentionally broken code
set -e

cd /workspace/ruff

# Remove the badly formatted code that was added in Dockerfile
# The bad code was appended to lib.rs, so we need to remove it

# First, let's see what we're working with
echo "Before fix - checking for bad code:"
grep -n "badly_formatted" crates/ruff_python_parser/src/lib.rs || echo "No bad code found"

# Remove lines containing the bad code (the last line added by Dockerfile)
# The bad code is at the end of the file, appended after the proper content
if grep -q "badly_formatted" crates/ruff_python_parser/src/lib.rs; then
    echo "Removing badly formatted code..."
    # Remove the last line(s) that contain the bad code
    # We need to remove the appended bad code
    head -n -1 crates/ruff_python_parser/src/lib.rs > /tmp/lib_rs_fixed.rs
    mv /tmp/lib_rs_fixed.rs crates/ruff_python_parser/src/lib.rs
fi

# Format the code to fix any remaining formatting issues
echo "Running cargo fmt..."
cargo fmt --all

echo "Fix applied successfully!"
